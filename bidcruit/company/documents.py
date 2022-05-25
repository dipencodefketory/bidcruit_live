
from django_elasticsearch_dsl import Document,fields
from django_elasticsearch_dsl.registries import registry
from accounts.models import User
import  candidate.models as candidate_models



@registry.register_document
class CandidateDocument(Document):
    # manufacturer = fields.ObjectField(properties={
    #     'name': fields.TextField(attr='get_manufacturer_name'),
    #     'country_code': fields.TextField(attr='get_manufacturer_country_code'),
    # })
    skills = fields.TextField(attr="get_skills")
    job_titles = fields.TextField(attr="get_job_titles")
    preferred_cities = fields.TextField(attr="get_preferred_cities")
    current_city =fields.TextField(attr="get_current_city")
    education_list = fields.TextField(attr="get_candidates_education_list")
    # total_experience = fields.TextField(attr="get_total_experience")
    # job_titles = fields
    # ads = fields.NestedField(properties={
    #     'description': fields.TextField(),
    #     'title': fields.TextField(),
    #     'pk': fields.IntegerField(),
    # })
    
    class Index:
        # Name of the Elasticsearch index
        name = 'bidcruit_search'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            
        ]
        # related_models = [Manufacturer, Ad]
        related_models =  ["candidate.models.CandidateSkillUserMap","candidate.models.CandidateProfile","candidate.models.CandidateEducation","candidate.models.CandidateExperience"]  # Optional: to ensure the Car will be re-saved when Manufacturer or Ad is updated


        
    # def get_queryset(self):
    #     """Not mandatory but to improve performance we can select related in one sql request"""
    #     return super(CarDocument, self).get_queryset().select_related(
    #         'manufacturer'
    #     )


        # if isinstance(related_instance, candidate_models.CandidateSkillUserMap):
        #     print("heeeeeyoooooooooooooooooooo")
        #     return "helloe"

# @registry.register_document
# class Skill(Document):

    
#     class Index:
#         # Name of the Elasticsearch index
#         name = 'skills'
#         # See Elasticsearch Indices API reference for available settings
#         settings = {'number_of_shards': 1,
#                     'number_of_replicas': 0}

#     class Django:
#         model = Skill
#         fields = [
#             'name',
            
#         ]


# def bulk_indexing():  
#     CandidateDocument.init()
#     es = Elasticsearch()   
#     bulk(client=es, actions=(b.indexing() for b in User.objects.all().iterator()))


