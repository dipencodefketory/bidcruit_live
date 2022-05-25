import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

import candidate
from .managers import UserManager
import random
from django.utils import timezone
# from candidate import models as candidate_models
# from company.documents import CandidateDocument


def generate_pk():
    number = random.randint(1000, 99999)
    return 'candidate-{}-{}'.format(timezone.now().strftime('%y%m%d'), number)


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
        is_superuser = None
        EMAIL_FIELD = "email"
        USERNAME_FIELD = 'email'

        objects = UserManager()

        email = models.EmailField(unique=True)
        company_name = models.CharField(max_length=100)
        first_name = models.CharField(max_length=50)
        last_name = models.CharField(max_length=50)
        website = models.CharField(max_length=100)
        is_staff = models.BooleanField(default=False)
        is_superuser = models.BooleanField(default=False)
        is_company = models.BooleanField(default=False)
        is_candidate = models.BooleanField(default=False)
        is_agency = models.BooleanField(default=False)
        is_active = models.BooleanField(default=False)
        status = models.BooleanField(default=False,null=True)
        ip = models.CharField(max_length=20)
        device_type = models.CharField(max_length=50)
        browser_type = models.CharField(max_length=50)
        browser_version = models.CharField(max_length=50)
        os_type = models.CharField(max_length=50)
        os_version = models.CharField(max_length=50)
        count = models.IntegerField(null=True, default=0)
        referral_number = models.CharField(max_length=20,null=True)
        referred_by = models.CharField(max_length=20,null=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        added_by = models.ForeignKey("self", models.CASCADE, default=None, null=True)

        if is_company == True:
                REQUIRED_FIELDS = ["company_name", "email", "websites"]

        if is_candidate == True:
                REQUIRED_FIELDS = ["first_name", "last_name", "email"]

        if is_agency == True:
                REQUIRED_FIELDS = ["email"]

        def __str__(self):
                return self.first_name

        def get_skills(self):
            try:
                active_profile = get_active_profile(self)

                candidate_skill_user_map = candidate_models.CandidateSkillUserMap.objects.filter(candidate_id=self,profile_id = active_profile.profile_id)
                skill_list = []
                for i in candidate_skill_user_map:
                    if i.skill.name not in skill_list:
                        skill_list.append(i.skill.name)
                print("skill list",skill_list)
                # print("skill list",candidate_skill_user_map)
                return ','.join(skill_list)
            except:
                print("skill exception")
                return None
        # return 'test dummy'

        def get_preferred_cities(self):
            try:
                candidate_profile = get_active_profile(self)
                preferred_cities = []
                city_ids = candidate_profile.preferred_cities
                city_ids = city_ids.split(',')
                for j in city_ids:
                    city = candidate_models.City.objects.get(id=j)
                    if city.city_name not in preferred_cities:
                        preferred_cities.append(city.city_name)
                return ','.join(preferred_cities)
            except:
                return "preferred cities exception"

        def get_job_titles(self):
            try:
                # works for single instance of candidate experience
                # candidate_experience = CandidateExperience.objects.filter(candidate_id=self.id)
                # return candidate_experience.Job_profile_name

     #           candidate_experience = candidate_models.CandidateExperience.objects.filter(candidate_id=self.id)
    #            job_titles=''
   #             for i in candidate_experience:
  #                  job_titles += i.job_profile_name +','
 #               print("job titles",job_titles)
#                return job_titles

                active_profile = get_active_profile(self)
                print("designation",active_profile.designation)
                return active_profile.designation
            except:
                print("job_title_exceptions")
                return None

        def get_candidates_education_list(self):
            try:
                candidate_education = candidate_models.CandidateEducation.objects.filter(candidate_id = self)
                education_list =''
                for i in candidate_education:
                    education_list += i.degree.name +','
                print("eeducaiton list",education_list)
                return education_list
            except:
                print("education exception")
                return None

        def get_total_experience(self):
            try:
                candidate_profile = candidate_models.CandidateProfile.objects.get(candidate_id=self)
                return candidate_profile.total_experience
            except:
                print("experience error")
                return None

        def get_current_city(self):
            try:
                profiles = candidate_models.Profile.objects.filter(candidate_id=self)
                for i in profiles:
                    if i.active == True:
                        active_profile = i
                candidate_profile = candidate_models.CandidateProfile.objects.get(profile_id=active_profile)
                print("current city",candidate_profile.city.city_name)
                return candidate_profile.city.city_name
            except:
                print("current city exception")
                return None

        def indexing(self):
            print('indexing method was called')
            obj = CandidateDocument(
                # meta={'id': self.id},
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                skills=self.get_skills(),
                job_titles=self.get_job_titles(),
                current_city = self.get_current_city(),
                preferred_cities = self.get_preferred_cities(),
                education_list  = self.get_candidates_education_list(),
            )
            obj.save()
            return obj.to_dict()


class LoginDetail(models.Model):
    user_id = models.ForeignKey(User, related_name="login", on_delete=models.CASCADE,null=True)
    # id = models.CharField(default=generate_pk, primary_key=True, max_length=255, unique=True)
    login_time = models.DateTimeField(max_length=200, auto_now_add=True)
    ip = models.CharField(max_length=20)
    device_type = models.CharField(max_length=50)
    browser_type = models.CharField(max_length=50)
    browser_version = models.CharField(max_length=50)
    os_type = models.CharField(max_length=50)
    os_version = models.CharField(max_length=50)
    otp = models.CharField(max_length=6)
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)

    def __str__(self):
        return str(self.id)

class VerifyCandidateEmail(models.Model):
    email=models.EmailField()
    otp=models.IntegerField()
    create_at = models.DateTimeField(max_length=200, auto_now_add=True)

#to avoid cyclic imports
from candidate import models as candidate_models
from company.documents import CandidateDocument



def get_active_profile(current_user):
    profiles = candidate_models.Profile.objects.filter(candidate_id=current_user)
    for i in profiles:
        if i.active == True:
            candidate_profile = candidate_models.CandidateProfile.objects.get(profile_id=i)
            return candidate_profile




