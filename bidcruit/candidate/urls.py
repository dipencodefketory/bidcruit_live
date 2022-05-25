from django.urls import path
from django.conf.urls import url
from . import views
from chat import views as chatview
app_name= 'candidate'

urlpatterns = [
    path('home/', views.index, name='home'),
    path('signup', views.ragister, name="signup"),
    path('signup/<str:referral>', views.referral_signup, name="referral_signup"),
    path('change_password/', views.change_password, name='change_password'),
    url(r'^country/(?P<id>\d+)/$', views.state_view),
    url(r'^state/(?P<id>\d+)/$', views.city_view),
    url(r'^cities_by_country/(?P<id>\d+)/$', views.cities_by_country),
    url(r'^preference_cities_by_country/(?P<id>\d+)/$', views.preference_cities_by_country),
    path('candidate_profile', views.candidate_profile, name="candidate_profile"),
    path('check_email_is_valid', views.check_email_is_valid, name="check_email_is_valid"),
    path('/<str:url>/', views.timeline, name="timeline"),
   
    # charts
    path('statistics/', views.statistics_view, name="candidate_statistics"),
    path('chart/filter-options/', views.get_filter_options, name='chart-filter-options'),
    path('chart/payment-method/', views.payment_method_chart, name='chart-payment-method'),
    path('chart/job-experience/', views.job_exp_Chart, name='chart-job-experience'),
    path('chart/edu-percentage/', views.edu_per_chart, name='chart-edu-percentage'),
    path('charts', views.charts, name='charts'),


    # Wizard
    path('upload_resume/personal_detail_temp', views.personal_detail_temp, name="personal_detail_temp"),
    path('upload_resume/education_temp', views.education_temp, name="education_temp"),
    path('upload_resume/work_experience_temp', views.work_experience_temp, name="work_experience_temp"),
    path('upload_resume/skill_temp', views.skill_temp, name="skill_temp"),
    path('upload_resume/other_temp', views.other_temp, name="other_temp"),
    path('upload_resume/remove_record', views.remove_record, name="remove_record"),
    path('upload_resume/save_resume', views.save_resume, name="save_resume"),
    path('create_resume_pass/', views.create_resume_pass, name="create_resume_pass"),
    path('update_resume_pass/', views.update_resume_pass, name="update_resume_pass"),
    path('update_share_url/',views.update_share_url,name="update_share_url"),
    path('check_sharing_url_is_valid',views.check_sharing_url_is_valid,name="check_sharing_url_is_valid"),

    # Dashboard
    path('upload_resume_add/<str:url>', views.upload_resume, name='upload_resume_add'),
    path('add_profile/',views.add_profile,name='add_profile'),
    path('add_profile_detail/<str:url>',views.add_profile_detail,name='add_profile_detail'),
    path('toggle_profile/', views.toggle_profile, name="toggle_profile"),
    path('toggle_field_state/', views.toggle_field_state, name="toggle_field_state"),
    path('edit_profile/<str:profile_id>', views.edit_profile, name="edit_profile"),
    path('job_preference/', views.candidate_job_preference, name="job_preference"),

    #  Request
    path('hire_request/', views.hire_request, name="hire_request"),
    path('accept_request/<str:profile_id>/<int:company_id>/<str:hire_id>', views.accept_request, name="accept_request"),
    path('reject_request/<str:profile_id>/<int:company_id>/<str:hire_id>', views.reject_request, name="reject_request"),
    path('data_accept_request/<str:profile_id>/<int:company_id>/<str:data_id>/', views.data_accept_request, name="data_accept_request"),
    path('data_reject_request/<str:profile_id>/<int:company_id>/<str:data_id>/', views.data_reject_request, name="data_reject_request"),

    path('file_download',views.file_download,name="file_download"),
    path('look_for_job_check/', views.look_for_job_check, name="look_for_job_check"),
    path('delete_exp_document', views.delete_exp_doc, name="delete_exp_doc"),
    path('candidate_resume_update/', views.candidate_resume_update, name="candidate_resume_update"),

    # Profile update
    # path('edit_profile/<str:profile_id>', views.edit_profile, name="edit_profile"),
    path('download_folder/<int:candidate_id>/',views.download_folder,name="download_folder"),
    path('test_redirect/', views.test_redirect, name="test_redirect"),


    path('job_view/', views.job_view, name='job_view'),
    path('basic_detail',views.basic_detail,name='basic_detail'),
    path('basic_detail/<int:cand_detail_id>',views.basic_detail,name='basic_detail'),
    #apply job
    path('add_apply_candidate/', views.add_apply_candidate, name='add_apply_candidate'),#Company
    path('apply_candidate/', views.apply_candidate, name='apply_candidate'),#agency
    path('applyed_jod_afterlogin/', views.applyed_jod_afterlogin, name='applyed_jod_afterlogin'),
    path('applied_job/<int:id>/',views.applied_job,name='applied_job'),
    path('applied_job_list/', views.applied_job_list, name='applied_job_list'),
    path('candidate_jcr/<int:id>/<int:job_id>', views.candidate_jcr, name='candidate_jcr'),
    path('applied_job_detail/<int:id>/<str:company_type>/', views.applied_job_detail, name='applied_job_detail'),
    path("prequisites_view/<int:id>/<int:job_id>", views.prequisites_view, name="prequisites_view"),
    # agency
    path("agency_prequisites_view/<int:id>/<int:job_id>", views.agency_prequisites_view, name="agency_prequisites_view"),

# CODING EXAM

    path("coding_test/<int:id>/<int:job_id>", views.coding_test, name="coding_test"),
    path('preview',views.preview,name='preview'),
    path('save_code/<int:template_id>/<int:job_id>', views.save_code, name='save_code'),
    path('save_front_end_code/<int:template_id>/<int:job_id>',views.save_front_end_code,name='save_front_end_code'),
    # agency
    path("agency_coding_test/<int:id>/<int:job_id>", views.agency_coding_test, name="agency_coding_test"),
    path('agency_preview',views.agency_preview,name='agency_preview'),
    path('agency_save_code/<int:template_id>/<int:job_id>', views.agency_save_code, name='agency_save_code'),
    path('agency_save_front_end_code/<int:template_id>/<int:job_id>',views.agency_save_front_end_code,name='agency_save_front_end_code'),
#     mcq
    path("mcq_exam/<int:id>/<int:job_id>", views.mcq_exam, name="mcq_exam"),
    path("mcq_exam_fill/<int:id>/<int:job_id>", views.mcq_exam_fill, name="mcq_exam_fill"),
    path("mcq_result/<int:id>/<int:job_id>", views.mcq_result, name="mcq_result"),

    # agency
    path("agency_mcq_exam/<int:id>/<int:job_id>", views.agency_mcq_exam, name="agency_mcq_exam"),
    path("agency_mcq_exam_fill/<int:id>/<int:job_id>", views.agency_mcq_exam_fill, name="agency_mcq_exam_fill"),
    path("agency_mcq_result/<int:id>/<int:job_id>", views.agency_mcq_result, name="agency_mcq_result"),

#   descriptive
    path("descriptive_exam/<int:id>/<int:job_id>", views.descriptive_exam, name="descriptive_exam"),
    path("descriptive_exam_fill/<int:id>/<int:job_id>", views.descriptive_exam_fill, name="descriptive_exam_fill"),
    path("descriptive_result/<int:id>/<int:job_id>", views.descriptive_result, name="descriptive_result"),
    # agency
    path("agency_descriptive_exam/<int:id>/<int:job_id>", views.agency_descriptive_exam, name="agency_descriptive_exam"),
    path("agency_descriptive_exam_fill/<int:id>/<int:job_id>", views.agency_descriptive_exam_fill, name="agency_descriptive_exam_fill"),
    path("agency_descriptive_result/<int:id>/<int:job_id>", views.agency_descriptive_result, name="agency_descriptive_result"),
#   Image
    path("image_exam/<int:id>/<int:job_id>", views.image_exam, name="image_exam"),
    path("image_exam_fill/<int:id>/<int:job_id>", views.image_exam_fill, name="image_exam_fill"),
    path("image_result/<int:id>/<int:job_id>", views.image_result, name="image_result"),
    # agency
    path("agency_image_exam/<int:id>/<int:job_id>", views.agency_image_exam, name="agency_image_exam"),
    path("agency_image_exam_fill/<int:id>/<int:job_id>", views.agency_image_exam_fill, name="agency_image_exam_fill"),
    path("agency_image_result/<int:id>/<int:job_id>", views.agency_image_result, name="agency_image_result"),    

#   audio
    path("audio_exam/<int:id>/<int:job_id>", views.audio_exam, name="audio_exam"),
    path("audio_exam_fill/<int:id>/<int:job_id>", views.audio_exam_fill, name="audio_exam_fill"),
    path("audio_result/<int:id>/<int:job_id>", views.audio_result, name="audio_result"),
    # agency
    path("agency_audio_exam/<int:id>/<int:job_id>", views.agency_audio_exam, name="agency_audio_exam"),
    path("agency_audio_exam_fill/<int:id>/<int:job_id>", views.agency_audio_exam_fill, name="agency_audio_exam_fill"),
    path("agency_audio_result/<int:id>/<int:job_id>", views.agency_audio_result, name="agency_audio_result"),

    path("agency_candidate_negotiate_offer/<int:id>", views.agency_candidate_negotiate_offer, name="agency_candidate_negotiate_offer"),
    path("custom_round/<int:id>", views.custom_round, name="custom_round"),
    path("company_profile/<int:id>", views.company_profile, name="company_profile"),
    path("list_of_agency_company/", views.list_of_agency_company, name="list_of_agency_company"),

    # withdraw_candidate
    path("withdraw_candidate/<str:user_type>/<int:id>/", views.withdraw_candidate, name="withdraw_candidate"),

# 
    path("refresh_detect/<int:id>", views.refresh_detect, name="refresh_detect"),
    # applicant_create_account
    path("applicant_create_account/<int:applicant_id>", views.applicant_create_account, name="applicant_create_account"),
    path("chat/", chatview.chatlist, name="chat"),


    path("notification_list/", views.notification_list, name="notification_list"),
    
    path("candidate_profile_settings/", views.candidate_profile_settings, name="candidate_profile_settings"),
    path("verify_detail/<int:applicantid>", views.verify_detail, name="verify_detail"),
    path("candidate_verify/<int:applicantid>", views.candidate_verify, name="candidate_verify"),
    
    
]

