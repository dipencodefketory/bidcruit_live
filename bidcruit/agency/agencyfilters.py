

import django_filters
from django_filters import DateFilter, CharFilter,NumberFilter,BooleanFilter,ModelMultipleChoiceFilter,ModelChoiceFilter
from .models import *
from candidate import models as CandidateModel
from django import forms
from django_select2.forms import ModelSelect2Widget,Select2MultipleWidget
BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
from django.db.models import Q
from django.db.models import IntegerField
from django.db.models.functions import Cast
def multiple_search(queryset, name, value):
    queryset = queryset.filter(Q(job_title__icontains=value) | Q(required_skill__name__icontains=value))
    return queryset

class JobFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(label='Keywoard Search', method=multiple_search)
    start_date = DateFilter(field_name="target_date",label='Target Star Date', lookup_expr='gte',widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = DateFilter(field_name="target_date",label='Target End Date', lookup_expr='lte',widget=forms.DateInput(attrs={'type': 'date'}))
    min_exp = NumberFilter(field_name="experience_year_min", lookup_expr='gte',label='Minimum Experience')
    max_exp = NumberFilter(field_name="experience_year_max", lookup_expr='lte',label='Maximum Experience')
    min_salary = NumberFilter(field_name="min_salary", lookup_expr='gte',label='Minimum Salary')
    max_salary = NumberFilter(field_name="max_salary", lookup_expr='lte',label='Minimum Salary')
    publish_start_date = DateFilter(field_name="publish_at",label='Publish Star Date', lookup_expr='gte',widget=forms.DateInput(attrs={'type': 'date'}))
    publish_end_date = DateFilter(field_name="publish_at",label='Publish End Date', lookup_expr='lte',widget=forms.DateInput(attrs={'type': 'date'}))
    job_type = ModelMultipleChoiceFilter(queryset=CandidateModel.JobTypes.objects.all(),label='Job Type',widget=forms.CheckboxSelectMultiple)
    industry_type = ModelChoiceFilter(queryset=CandidateModel.IndustryType.objects.all(),label='Industry Type')
    remote_job = BooleanFilter(label='Remote job',widget=forms.RadioSelect(choices=[(True, 'Yes'),(False, 'No')]))
    salary_as_per_market = BooleanFilter(label='Salary As Per Market',widget=forms.RadioSelect(choices=[(True, 'Yes'),(False, 'No')]))
    # required_skill = ModelMultipleChoiceFilter(queryset = CandidateModel.Skill.objects.all(),label='Skill',widget=Select2MultipleWidget(
    #                               attrs={'data-placeholder': 'Please choose Skill'} ))
    job_shift_id = ModelMultipleChoiceFilter(queryset=CandidateModel.JobShift.objects.all(),label='Job Shift',widget=forms.CheckboxSelectMultiple)
    country = CharFilter(label='Country', field_name='country__country_name', lookup_expr='icontains')
    class Meta:
        model = JobCreation
        fields = ['department']
        
def designation_search(queryset, name, value):
    queryset = queryset.filter(Q(designation__icontains=value))
    return queryset
# def total_exper_min(queryset, name, value):
#     queryset = queryset.filter(Q(total_exper_as_int=Cast('total_exper',IntegerField())<=value))
#     return queryset
# def total_exper_max(queryset, name, value):
#     queryset = queryset.filter(Q(total_exper_as_int=Cast('total_exper',IntegerField())<=value))
#     return queryset
class CandidateFilter(django_filters.FilterSet):
    # categories=CharFilter(label='Category Search', method=category_search)
    # tags = CharFilter(label='Tags Search', method=tags_search)
    designation = django_filters.CharFilter(label='Designation Search', method=designation_search)
    notice = ModelMultipleChoiceFilter(queryset=CandidateModel.NoticePeriod.objects.all(),label='Notice Period',widget=forms.CheckboxSelectMultiple)
    source = ModelMultipleChoiceFilter(queryset=CandidateModel.Source.objects.all(),label='Source By',widget=forms.CheckboxSelectMultiple)
    # categories=ModelMultipleChoiceFilter(queryset=CandidateCategories.objects.all(),label='category',widget=Select2MultipleWidget())
    categories = ModelChoiceFilter(queryset=CandidateCategories.objects.all(),label='Category')
    current_city = ModelChoiceFilter(queryset=CandidateModel.City.objects.all(),label='Current City')
    min_current_salary = NumberFilter(field_name="ctc", lookup_expr='gte',label='Minimum Salary(Current)')
    max_current_salary = NumberFilter(field_name="ctc", lookup_expr='lte',label='Minimum Salary(Current)')
    min_expected_salary = NumberFilter(field_name="expectedctc", lookup_expr='gte',label='Minimum Salary(Expected)')
    max_expected_salary = NumberFilter(field_name="expectedctc", lookup_expr='lte',label='Minimum Salary(Expected)')
    # total_exper_min = NumberFilter(field_name="total_exper", lookup_expr='gte',label='Minimum Total Experiance',method=total_exper_min)
    # total_exper_max = NumberFilter(field_name="total_exper", lookup_expr='lte',label='Maximum Total Experiance')
    class Meta:
        model = InternalCandidateBasicDetail
        fields = ['first_name','last_name','email','contact']
