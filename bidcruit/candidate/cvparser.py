import logging
import re

import docx2txt

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from io import StringIO

from commonregex import street_address

import datefinder
import datetime

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from elasticsearch import Elasticsearch
import sqlite3

conn = sqlite3.connect('respars.sqlite3')
skills_list = [s[1] for s in conn.execute("SELECT * FROM SKILLS")]
ignore_words = [iw[0] for iw in conn.execute("SELECT IgnoreWord FROM ignore_words")]
conn.close()


logging.basicConfig(level=logging.ERROR)

objective = (
    'career goal',
    'objective',
    'career objective',
    'employment objective',
    'professional objective',
    'summary',
    'career summary',
    'professional summary',
    'summary of qualifications',
)

work_and_employment = (
    'employment history',
    'work history',
    'work experience',
    'experience',
    'professional experience',
    'professional background',
)
project=(
    'projects',
    'project',
    # 'work history',
    # 'work experience',
    # 'additional experience',
    # 'career related experience',
    # 'related experience',
    # 'programming experience',
    # 'freelance',
    # 'freelance experience',
    # 'army experience',
    # 'military experience',
    # 'military background',
)

education_and_training = (
    'academic background',
    'academic experience',
    'programs',
    'courses',
    'related courses',
    'education',
    'educational background',
    'educational qualifications',
    'educational training',
    'education and training',
    'training',
    'academic training',
    'professional training',
    'course project experience',
    'related course projects',
    'internship experience',
    'internships',
    'apprenticeships',
    'college activities',
    'certifications',
    'special training',
)

skills_header = (
    'credentials',
    'qualifications',
    'areas of experience',
    'areas of expertise',
    'areas of knowledge',
    'skills',
    'career related skills',
    'professional skills',
    'specialized skills',
    'technical skills',
    'computer skills',
    'computer knowledge',
    'software',
    'technologies',
    'technical experience',
    'proficiencies',
    'languages',
    'language competencies and skills',
    'programming languages',
)

misc = (
    'activities and honors',
    'affiliations',
    'professional affiliations',
    'associations',
    'professional associations',
    'memberships',
    'professional memberships',
    'athletic involvement',
    'community involvement',
    'civic activities',
    'extra-Curricular activities',
    'professional activities',
    'volunteer work',
    'volunteer experience',
)

accomplishments = (
    'licenses',
    'presentations',
    'conference presentations',
    'conventions',
    'dissertations',
    'exhibits',
    'papers',
    'publications',
    'professional publications',
    'research',
    'research grants',
    'research projects',
    'current research interests',
    'thesis',
    'theses',
)


def process(file):
    """
    Main function to process resume file to json.
    :param file: Resume file
    :return: resume_data: Parsed resume dictionary
    """
    if file.name.endswith('pdf'):
        resume_lines = convert_pdf_to_txt(file)
    else:
        return None

    resume_segments = segment(resume_lines)

    resume_data = {
        'contact_info': get_contact_info(resume_lines),
        'education': extract_edu_info(resume_segments, resume_lines[:]),
        # 'degree': extract_degree_info(resume_segments, resume_lines[:]),
        'work_history': extract_company_info(resume_segments, resume_lines[:]),
        'skills': extract_skills(resume_segments, resume_lines[:]),
    }
    print(resume_data)
    return resume_data


def segment(string_to_search):
    resume_segments = {
        'objective': {},
        'work_and_employment': {},
        'education_and_training': {},
        'project':{},
        'skills': {},
        'accomplishments': {},
        'misc': {}
    }

    resume_indices = []

    find_segment_indices(string_to_search, resume_segments, resume_indices)
    slice_segments(string_to_search, resume_segments, resume_indices)

    return resume_segments


def find_segment_indices(string_to_search, resume_segments, resume_indices):
    for i, line in enumerate(string_to_search):

        if line[0].islower():
            continue

        header = line.lower()
        if [o for o in objective if header.startswith(o)]:
            resume_indices.append(i)
            header = [o for o in objective if header.startswith(o)][0]
            resume_segments['objective'][header] = i
        elif [w for w in work_and_employment if header.startswith(w)]:
            resume_indices.append(i)
            header = [w for w in work_and_employment if header.startswith(w)][0]
            resume_segments['work_and_employment'][header] = i
        elif [p for p in project if header.startswith(p)]:
            resume_indices.append(i)
            header = [p for p in project if header.startswith(p)][0]
            resume_segments['project'][header] = i
        elif [e for e in education_and_training if header.startswith(e)]:
            resume_indices.append(i)
            header = [e for e in education_and_training if header.startswith(e)][0]
            resume_segments['education_and_training'][header] = i
        elif [s for s in skills_header if header.startswith(s)]:
            resume_indices.append(i)
            header = [s for s in skills_header if header.startswith(s)][0]
            resume_segments['skills'][header] = i
        elif [m for m in misc if header.startswith(m)]:
            resume_indices.append(i)
            header = [m for m in misc if header.startswith(m)][0]
            resume_segments['misc'][header] = i
        elif [a for a in accomplishments if header.startswith(a)]:
            resume_indices.append(i)
            header = [a for a in accomplishments if header.startswith(a)][0]
            resume_segments['accomplishments'][header] = i


def slice_segments(string_to_search, resume_segments, resume_indices):
    try:
        resume_segments['contact_info'] = string_to_search[:resume_indices[0]]
        for section, value in resume_segments.items():
            if section == 'contact_info':
                continue
            for sub_section, start_idx in value.items():
                end_idx = len(string_to_search)
                if (resume_indices.index(start_idx) + 1) != len(resume_indices):
                    end_idx = resume_indices[resume_indices.index(start_idx) + 1]
                resume_segments[section][sub_section] = string_to_search[start_idx:end_idx]
    except Exception as e:
        logging.error('Error in data file:: ' + str(e))
        return None


def get_contact_info(resume_segments):
    """
    Constructs and returns contact_info dictionary.
    :param resume_segments: Dictionary of segmented resume data
    :return: contact_info: Dictionary containing contact info
    """
    contact_detail={'email':'','phone':'','address':'','state':''}
    string_to_search = resume_segments
    email_pattern = re.compile(r"^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$", re.IGNORECASE)
    for line in string_to_search:
        # print(type(line))
        result = re.search(email_pattern, str(line))
        if result:
            print(line)
            # result_groups = result.group()
            contact_detail['email']=line
        # else:
        #     contact_detail['email']=''
# Contact number
    string_to_search = resume_segments
    regular_expression = re.compile(r"(\+91)?\s*?(\d{3})\s*?(\d{3})\s*?(\d{3})",  # 4 digit local
                                        re.IGNORECASE)
    for line in string_to_search:
        result = re.search(regular_expression, line)
        if result:
            phone_no = result.groups()
            # phone_no = "".join(result_groups)
            contact_detail['phone']=phone_no
        # else:
        #     contact_detail['phone']=''

    
# address
    string_to_search = resume_segments
    for line in string_to_search:
        result = re.search(street_address, line)
        if result:
            str_addr = result.group().strip(',')
            contact_detail['address']=str_addr
        # else:
            # contact_detail['address']=''
    
# state
    string_to_search = resume_segments
    states = ['AK', 'GUJARAT','AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID',
                  'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE',
                  'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
                  'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    state_pattern = re.compile(r'\b(' + '|'.join(states) + r')\b')
    for line in string_to_search:
        result = state_pattern.search(line)
        if result:
            contact_detail['state']=result.group()
        # else:
        #     contact_detail['state']=''
    print(contact_detail)
    return contact_detail
    


def _process_txt(tokens, stop_words):
    return ' '.join([word for word in tokens if word not in stop_words])


def _flatten_dict(list_dict):
    list_values = []
    for key, val in list_dict.items():
        if isinstance(val, list):
            list_values += val

    return list_values


# def _get_date_range(string_to_search, start_idx):
#     resume_len = len(string_to_search)
#     text_to_search = string_to_search[start_idx]
#     if (start_idx + 1) < resume_len:
#         text_to_search = text_to_search + ' ' + string_to_search[start_idx + 1]
#         if (start_idx + 2) < resume_len:
#             text_to_search = text_to_search + ' ' + string_to_search[start_idx + 2]

#     # list of dates found
#     dates = list(datefinder.find_dates(text_to_search))
#     # Sanity test for dates
#     dates = [date for date in dates
#              if datetime.datetime(year=1960, month=1,day=1) < date < datetime.datetime.today()]

#     return dates


def convert_pdf_to_txt(pdf_file):
    """
    A utility function to convert a machine-readable PDF to raw text.

    This code is largely borrowed from existing solutions, and does not match the style of the rest of this repo.
    :param input_pdf_path: Path to the .pdf file which should be converted
    :type input_pdf_path: str
    :return: The text contents of the pdf
    :rtype: str
    """
    try:
        # PDFMiner boilerplate
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Iterate through pages
        for page in PDFPage.get_pages(pdf_file, set(), maxpages=0, password='',
                                      caching=True, check_extractable=True):
            interpreter.process_page(page)
        device.close()

        # Get full string from PDF
        full_string = retstr.getvalue()
        retstr.close()

        # Normalize a bit, removing line breaks
        full_string = full_string.replace("\r", "\n")
        full_string = full_string.replace("\t", " ")

        # Remove awkward LaTeX bullet characters
        full_string = re.sub(r"\(cid:\d{0,2}\)", " ", full_string)

        # Split text blob into individual lines
        resume_lines = full_string.splitlines(True)

        # Remove empty strings and whitespaces
        resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]

        return resume_lines

    except Exception as e:
        logging.error('Error in pdf file:: ' + str(e))
        return []


def extract_edu_info(resume_segments, string_to_search):
    edu={}
    try:
        # es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        universities = []
        university_words = ('university', 'institute', 'college','school')
        university_word = ('bachelor of business administration')
        degrees = []
        gread=[]
        edu_info = resume_segments['education_and_training']
        # print(edu_info)
        conn = sqlite3.connect('respars.sqlite3')
        degree_list = [s[0] for s in conn.execute("SELECT * FROM degree")]
        universities_list = [s[0] for s in conn.execute("SELECT * FROM universities")]
        college_list = [s[0] for s in conn.execute("SELECT * FROM colleges")]
        edu_final=[]
        
        a=1
        education={}
        count_edu=[]
        for l,m in edu_info.items():
            for j in m:#line
                for degrees in degree_list:
                    if degrees in j:
                        count_edu.append(degrees)
                for g in range(len(count_edu)):
                    education[str(g+1)]={'degree':'','universities':'','college_scholl':'','Gread_percentage':'','start_date':'','end_date':''}
        # print(education)
        for l,m in edu_info.items():
            for j in m:
                for degrees in degree_list:
                    if degrees in j:
                        education[str(a)]['degree']=degrees
                        # l1.append(degrees)
                for universities in universities_list:
                    if universities in j:
                        education[str(a)]['universities']=universities
                        # l1.append(universities)
                for college in college_list:
                    if college in j:
                        education[str(a)]['college_scholl']=college
                        # l1.append(universities)
                # a = re.findall("\d+\.\d+",j)
                # for i in a:
                #     if float(i)<=10.00:
                #         gread.append(str(i)+' CGPA')
                #     else:
                #         gread.append(str(i)+' %')
                #     education[str(a)]['Gread_percentage']==gread
                if re.findall('(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s-]\d{2,4}',j.lower()):
                    aa= re.findall('(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s-]\d{2,4}|present',j.lower())
                    education[str(a)]['start_date']=aa[0]
                    education[str(a)]['end_date']=aa[1]
                    if  len(count_edu)>=a: 
                        print('1111111111111111111111111111111',education)
                        a+=1
                    # a+=1
                    # l1.append(aa[0])
                    # l1.append(aa[1])
                elif re.findall('(?:01|02|03|04|05|06|07|08|09|10|11|12)[/]\d{2,4}',j.lower()):
                    aa= re.findall('(?:01|02|03|04|05|06|07|08|09|10|11|12)[/]\d{2,4}|present',j.lower())
                    education[str(a)]['start_date']=aa[0]
                    education[str(a)]['end_date']=aa[1]
                    if  len(count_edu)>a: 
                        print('222222222222222222222222222222222222',education)  
                        a+=1
                elif re.findall('(?:1|2|3|4|5|6|7|8|9|0|1|2)[/]\d{2,4}',j.lower()):
                    aa= re.findall('(?:1|2|3|4|5|6|7|8|9|0|1|2)[/]\d{2,4}|present',j.lower())
                    education[str(a)]['start_date']=aa[0]
                    education[str(a)]['end_date']=aa[1]
                    if  len(count_edu)>a:   
                        print('33333333333333333333333333333333333333',education)
                        a+=1
                if re.findall('\d{2,4}',j.lower()):
                    aa= re.findall('\d{2,4}|present',j.lower())
                    if len(list(aa))<2:
                        education[str(a)]['end_date']=aa[0]
                    else:
                        education[str(a)]['start_date']=aa[0]
                        education[str(a)]['end_date']=aa[1]
                    if  len(count_edu)>a:   
                        a+=1
                    else:
                        continue
        return education

    except Exception as e:
        logging.error('Issue extracting education info:: ' + str(e))
        return []


    except Exception as e:
        logging.error('Issue extracting degree info:: ' + str(e))
        return []


def extract_company_info(resume_segments, string_to_search):
    try:
        # es = Elasticsearch()
        company_dict={}
        companies = []
        spl_chars = ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}']
        company_suffixes = ["corporation", "company", "incorporated", "limited", "co", "ltd",
                            "corp", "inc", "llc", "lc", "llp", "psc", "pllc", "plc"]
        conn = sqlite3.connect('respars.sqlite3')
        companies_list = [s[0] for s in conn.execute("SELECT * FROM companies")]
        work_info = resume_segments['work_and_employment']
        experiance_final=[]
        
        a=1
        company={}
        count_company=[]
        for l,m in work_info.items():
            for j in m:#line
                for companies in companies_list:
                    if companies in j:
                        count_company.append(companies)
                for g in range(len(count_company)):
                    company[str(g+1)]={'title':'','company_name':'','start_date':'','end_date':''}
        for l,m in work_info.items():
            for j in m:#line
                for title in ['developer','trainee']:
                    if title in j.lower():
                        company[str(a)]['title']=title
                for companies in companies_list:
                    if companies in j:
                        company[str(a)]['company_name']=companies

                if re.findall('(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s-]\d{2,4}',j.lower()):
                    aa= re.findall('(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s-]\d{2,4}|present',j.lower())
                    company[str(a)]['start_date']=aa[0]
                    company[str(a)]['end_date']=aa[1]
                    if  len(count_company)>a: 
                        a+=1
                elif re.findall('(?:01|02|03|04|05|06|07|08|09|10|11|12)[/]\d{2,4}',j.lower()):
                    aa= re.findall('(?:01|02|03|04|05|06|07|08|09|10|11|12)[/]\d{2,4}|present',j.lower())
                    company[str(a)]['start_date']=aa[0]
                    company[str(a)]['end_date']=aa[1]
                    if  len(count_company)>a:   
                        a+=1
                elif re.findall('(?:1|2|3|4|5|6|7|8|9|0|1|2)[/]\d{2,4}',j.lower()):
                    aa= re.findall('(?:1|2|3|4|5|6|7|8|9|0|1|2)[/]\d{2,4}|present',j.lower())
                    company[str(a)]['start_date']=aa[0]
                    company[str(a)]['end_date']=aa[1]
                    if  len(count_company)>a:   
                        a+=1



        project_info = resume_segments['project']
        # print('=======================',project_info)
       
        return company

    except Exception as e:
        logging.error('Issue extracting company info:: ' + str(e))
        return []


def extract_skills(resume_segments, string_to_search):
    skills_dict = resume_segments['skills']
    if skills_dict:
        string_to_search = _flatten_dict(skills_dict)

    stop_words = set(stopwords.words('english'))
    stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])
    found_skills = []
    for line in string_to_search:
        processed_text = [text.lower() for text in word_tokenize(line) if text not in stop_words]
        found_skills += [s for s in skills_list if s.lower() in processed_text and s not in found_skills]

    skill_count = {}
    for skill in found_skills:
        skill_count[skill] = found_skills.count(skill)

    # print("\n===============\n" + str(skill_count) + "\n===============\n")
    print(set(found_skills))
    return list(set(found_skills))


