from os import execl
from django import forms
from candidate.models import City, Degree, NoticePeriod



notice_periods= NoticePeriod.objects.all()
notice_period_choices=[]

for i in notice_periods:
    notice_period_choices.append((i.id,i.notice_period))

# cities= City.objects.all()
# city_names =[]
# for i in cities:
#     city_names.append((i.id,i.city_name))
# city_names=[]
# education_choices= []
class CandidateForm(forms.Form):

    notice_period = ((1,'One Day'),(2,'Two Days'),(3,'Three Days'),(4,'Four Days'),(5,'Five Days'),(6,'Six Days'))
    include_skills = forms.ChoiceField(choices=[],required=False,label='Skills you want in your candidate',widget=forms.Select(attrs={'class': 'form-select select2_skill','multiple':'multiple','style':'width:100%'}))
    exclude_skills = forms.ChoiceField(choices=[],required=False,label='Skills you don\'t want in your candidate',widget=forms.Select(attrs={'class': 'form-select select2_skill','multiple':'multiple','style':'width:100%'}))
    notice_period =forms.ChoiceField(required=False,label='Notice Period',choices = notice_period_choices,widget=forms.Select(attrs={'class':'form-select select2'}))
    preferred_cities = forms.ChoiceField(required=False,label='Preferred cities',widget=forms.Select(attrs={'class': 'form-select select2_cities','multiple':'multiple','style':'width:100%'}))
    minimum_experience = forms.IntegerField(required=False,label='Minimum experience',widget=forms.NumberInput(attrs={'class': 'form-control'}))
    maximum_experience = forms.IntegerField(required=False,label='Maximum experience',widget=forms.NumberInput(attrs={'class': 'form-control'}))
    current_city = forms.ChoiceField(choices=[],required=False,label='Current City',widget=forms.Select(attrs={'class': 'form-select select2_cities','style':'width:100%'}))
    # working_company = forms.CharField(required=False,label='Working company',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))
    education = forms.ChoiceField(choices=[],required=False,label='Education',widget=forms.Select(attrs={'class': 'form-control select2_degrees','multiple':'multiple','style':'width:100%'}))

    def __init__(self, current_city=None,minimum_experience=None,maximum_experience=None,education_choices=None,preferred_cities= None,include_skills= None,exclude_skills= None,notice_period = None, *args, **kwargs):
        super(CandidateForm, self).__init__(*args, **kwargs)
        if current_city:
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',current_city)
            self.fields['current_city'].choices = current_city
        if minimum_experience:
            self.fields['minimum_experience'].initial = minimum_experience
        if maximum_experience:
            self.fields['maximum_experience'].initial = maximum_experience
        # if education_choices:
        #     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",education_choices)
        #     self.fields['education'].choices = education_choices
        if education_choices:
            print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",education_choices)
            print(self.fields['education'].choices)
            self.fields['education'].choices =  education_choices
            self.fields['education'].initial = education_choices
            # self.fields['education'].initial = education_choices\
            # self.initial['education'] = education_choices
            print(self.fields['education'].choices)
            print(self.fields['education'])
        if preferred_cities:
            self.fields['preferred_cities'].choices = preferred_cities
        if include_skills:
            options = []
            for i in include_skills:
                options.append((i,i))
            self.fields['include_skills'].choices = options
        if exclude_skills:
            options = []
            for i in exclude_skills:
                options.append((i,i))
            self.fields['exclude_skills'].choices = options
        if notice_period:
            self.fields['notice_period'].initial = notice_period

# 
# class CandidateForm(forms.Form):
#     notice_period = ((1,'One Day'),(2,'Two Days'),(3,'Three Days'),(4,'Four Days'),(5,'Five Days'),(6,'Six Days'))
#     include_skills = forms.CharField(label='Skills you want in your candidate', max_length=100,widget=forms.TextInput(attrs={'class': 'form-control js-example-basic-multiple js-states'}))
#     exclude_skills = forms.CharField(label='Skills you want in your candidate', max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))
#     notice_period =forms.ChoiceField(label='Notice Period',choices = notice_period,widget=forms.Select(attrs={'class':'form-select'}))
#     preferred_cities = forms.CharField(label='Preferred cities',max_length=40,widget=forms.TextInput(attrs={'class': 'form-control'}))
#     minimum_experience = forms.IntegerField(label='Minimum experience')
#     maximum_experience = forms.IntegerField(label='Maximum experience')
#     current_city = forms.CharField(label='Current City',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))
#     working_company = forms.CharField(label='Working company',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))
#     education = forms.CharField(label='education',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))

