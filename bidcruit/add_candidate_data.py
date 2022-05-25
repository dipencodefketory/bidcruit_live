import os
import django
import random
from faker import Faker
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE','bidcruit.settings')
django.setup()

from candidate.models import *
from accounts.models import User

fakeGen = Faker()
skills = ['html','css','javascript','django','python','php','ruby','Fortran']
skill_length = len(skills)


def get_random_skills():
    skill_no = random.randint(1,skill_length/2)
    random_skills = random.sample(skills,k=skill_no)
    return random_skills

def get_random_degrees():
    degrees = Degree.objects.all()
    random_degree = random.choice(degrees)
    return random_degree

def get_random_state():
    states =State.objects.all()
    random_state= random.choice(states)
    return random_state

def get_random_city():
    cities = City.objects.all()
    random_city = random.choice(cities)
    return random_city


def get_random_cities():
    x =City.objects.all()
    length =len(x)
    temp = random.randint(1,length)
    cities = City.objects.all().order_by('?')[:temp]
    
    city_list= []
    for i in cities:
        city_list.append(i.city_name)
    
    return ','.join(city_list)


jobs = ["Full stack developer","Backend developer","Ruby on Rails Developer","PHP developer","Java Developer","Fresher"]

def generate_candidate():


    #USER DATA
    first_name = fakeGen.first_name()
    last_name = fakeGen.last_name()
    email = fakeGen.email()
    company_name = 'codefaktory'
    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        company_name = company_name
    )
    

    #skills
    skill_list = get_random_skills()
    skill_list_string =','.join(skill_list)
    skill_item = Skill.objects.create(name=skill_list_string)
    
    candidate_skill_user_map = CandidateSkillUserMap.objects.create(candidate_id=user,skill = skill_item)

    
    # candidate_skill_user_map.skill.id = skill_item.id
    # candidate_skill_user_map.candidate_id = user.id
    candidate_skill_user_map.record_id = random.randint(0,1000)
    candidate_skill_user_map.start_year = 0
    candidate_skill_user_map.end_year = 2021
    candidate_skill_user_map.level = 10
    candidate_skill_user_map.update_at =datetime.datetime.now()
    candidate_skill_user_map.save()

    random_degree = get_random_degrees()



    #CANDIDATE EDUCATION
    candidate_education =CandidateEducation(candidate_id=user,degree=random_degree)
    candidate_education.field ="computer science"
    candidate_education.grade = 10
    candidate_education.start_date =0  
    candidate_education.end_date =2021
    candidate_education.certificate = 'lol.jpg'
    candidate_education.gap_count =0
    candidate_education.gap_description ='none'
    candidate_education.summary ='fresher'
    candidate_education.create_at =datetime.datetime.now()
    candidate_education.record_id =random.randint(0,10000)
    candidate_education.update_at =datetime.datetime.now()
    candidate_education.save()

    #CANDIDATE_EXPERIENCE
    experience = CandidateExperience.objects.create(candidate_id = user)
    job =random.choice(jobs)
    print("job",job)
    experience.job_profile_name=job
    experience.start_date =2000
    experience.start_date =2020
    experience.start_salary = 0
    experience.end_salary = 100000000
    experience.job_description_responsibility ="WORK IN OFFICE"
    experience.website ="WW.GOOGLE.COM"
    experience.gap_count =0
    experience.document ='lol.jpg'
    experience.gap = 0
    experience.record_id =1221
    experience.create_at =datetime.datetime.now()
    experience.update_at = datetime.datetime.now()
    experience.save()


    #CANDIDATE PROFILE

    random_state = get_random_state()
    random_city = get_random_city()
    candidate_profile = CandidateProfile.objects.create(candidate_id=user,state=random_state,city=random_city)
    candidate_profile.contact_no ='1234567890'
    candidate_profile.address  ='home'
    candidate_profile.dob = '1/2/2000'
    candidate_profile.subtitle = 'fresher'
    candidate_profile.website = 'www.home.com'
    candidate_profile.url_name = 'fake url'
    candidate_profile.current_salary = 0
    candidate_profile.expected_salary_min = 0
    candidate_profile.expected_salary_max = 10000
    candidate_profile.total_experience =random.randint(0,10)
    random_cities = get_random_cities()
    # candidate_profile.preferred_cities =random_cities
    candidate_profile.qr_code = 'lol.jpg'
    candidate_profile.create_at =datetime.datetime.now()
    candidate_profile.update_at =datetime.datetime.now()
    candidate_profile.save()




for i in range(1000):
    generate_candidate()
    print("Candidate ",i,"generated")
