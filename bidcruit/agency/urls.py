from django.urls import path
from django.conf.urls import url
from . import views
from chat import views as chatview
app_name= 'agency'

urlpatterns = [
    path('dashbord/', views.dashbord, name='dashbord'),
    path('agency_Profile', views.agency_Profile, name="agency_Profile"),
    path('agency_profile_update/<int:id>/', views.agency_profile_update, name="agency_profile_update"),
    path('agency_type/', views.agency_type, name="agency_type"),
    path('signup_freelancer/', views.signup_freelancer, name="signup_freelancer"),
    path('signup_agency/', views.signup_agency, name="signup_agency"),
    path('change_password/', views.change_password, name='change_password'),
    # ############################## ATS ####################################

    #   Candidates
    path('all_countries/', views.all_countries, name='all_countries'),
    path('all_states/<str:country_id>', views.all_states, name='all_states'),
    path('all_cities/<str:state_id>', views.all_cities, name='all_cities'),
    # path('add_candidate/', views.add_candidate, name='add_candidate'),
    path('all_candidates/', views.all_candidates, name='all_candidates'),
    path('view_candidate/<str:candidate_id>', views.view_candidate, name='view_candidate'),
    path('internal_candidate_notes/', views.internal_candidate_notes, name='internal_candidate_notes'),
    path("get_candidate_categories/", views.get_candidate_categories, name="get_candidate_categories"),
    path('verify_candidate/<int:id>', views.verify_candidate, name="verify_candidate"),
    path('get_tags/',views.get_tags,name='get_tags'),
   
    
    
# add client
    path('add_client/',views.add_client,name="add_client"),
    path('edit_client/<int:client_id>/',views.add_client,name="edit_client"),
    path('client_detail_view/<int:client_id>/',views.client_detail_view,name="client_detail_view"),
    path('delete_client/',views.delete_client,name="delete_client"),
    path('get_exists_client/',views.get_exists_client,name="get_exists_client"),

    # path('agency_registration/', views.agency_registration, name="agency_registration"),
    # path('agency_home/', views.agency_home, name="agency_home"),
    path('get_companies/', views.get_companies, name="get_companies"),
    path('invite_client/', views.invite_client, name="invite_client"),
    path('client_list',views.client_list,name='client_list'),
    path('all_connection',views.all_connection,name='all_connection'),
    path('active_connection_view/<int:id>/',views.active_connection_view,name='active_connection_view'),
    
   
    path('dept_add_or_update_view/',views.dept_add_or_update_view,name='dept_add_or_update_view'),
    path('delete_department/',views.delete_department,name='delete_department'),
    path('get_department/',views.get_department,name='get_department'),

    # category
    path('category_add_or_update_view/',views.category_add_or_update_view,name='category_add_or_update_view'),
    path('delete_candidatecategory/',views.delete_candidatecategory,name='delete_candidatecategory'),
    path('get_candidate_category/',views.get_candidate_category,name='get_candidate_category'),
    # internal User
    path('add_internal_user',views.add_internal_user,name="add_internal_user"),
    path('internal_user_list',views.internal_user_list,name="internal_user_list"),
    path('internal_user_view/<int:id>/',views.internal_user_view,name='internal_user_view'),
    path('update_internal_user/<int:id>/',views.update_internal_user,name='update_internal_user'),
    
    path('job_request_table',views.job_request_table,name="job_request_table"),
    path('job_view/<int:id>/',views.request_job_view,name="request_job_view"),
    path('job_openings_table/', views.job_openings_table, name='job_openings_table'),

    path('all_candidates',views.all_candidates,name="all_candidates"),
    path('add_internal_candidate_basic_detail',views.add_internal_candidate_basic_detail,name="add_internal_candidate_basic_detail"),
    path('add_internal_candidate_basic_detail/<int:int_cand_detail_id>',views.add_internal_candidate_basic_detail,name="add_internal_candidate_basic_detail"),

    path('check_candidate_email_is_valid',views.check_candidate_email_is_valid,name="check_candidate_email_is_valid"),
    path('check_candidate_customid_is_valid',views.check_candidate_customid_is_valid,name="check_candidate_customid_is_valid"),
    path("redact_resume/<int:internal_candidate_id>/",views.redact_resume,name="redact_resume"),
    path("save_redacted_resume/<int:internal_candidate_id>/",views.save_redacted_resume,name="save_redacted_resume"),


    # associate_job
    path('associate_job/<int:candidate_id>', views.associate_job, name='associate_job'),
    path("submit_candidate/<int:id>", views.submit_candidate, name="submit_candidate"),

    # Role Permission
    path('role_permission/',views.role_permission,name='role_permission'),
    path('role_list/',views.role_list,name='role_list'),
    path('role_permission_update/<int:id>/',views.role_permission_update,name='role_permission_update'),

    # APPLIED CANDIDATES VIEW
    path('applied_candidates_view/<int:id>', views.applied_candidates_view, name='applied_candidates_view'),
    path('company_portal_candidate_tablist/<int:candidate_id>/<int:job_id>',views.company_portal_candidate_tablist,name='company_portal_candidate_tablist'),

    path("change_employee_status/", views.change_employee_status, name="change_employee_status"),
    path("change_role_status/", views.change_role_status, name="change_role_status"),
    path("change_department_obj_status/", views.change_department_obj_status, name="change_department_obj_status"),
    path("candidate_request/", views.candidate_request, name="candidate_request"),
    path("request_for_detail_action/<int:internalid>/<int:candidateid>/", views.request_for_detail_action, name="request_for_detail_action"),


    # tracker
    path("tracker/", views.tracker, name="tracker"),
    path("chat/", chatview.chatlist, name="chat"),


    # mcq
    path('mcq_add_subject/',views.mcq_add_subject,name='mcq_add_subject'),
    path('mcq_update_subject/',views.mcq_update_subject,name='mcq_update_subject'),
    path('mcq_delete_subject/',views.mcq_delete_subject,name='mcq_delete_subject'),
    path('mcq_subject_list/',views.mcq_subject_list,name='mcq_subject_list'),
    path('preview_mcq/<int:id>',views.preview_mcq,name='preview_mcq'),
    path('add_mcq/<int:id>',views.add_mcq,name='add_mcq'),
    path('mcq_delete_question/',views.mcq_delete_question,name='mcq_delete_question'),
    path('update_mcq_question/',views.update_mcq_question,name='update_mcq_question'),
    path('get_mcq_question/',views.get_mcq_question,name='get_mcq_question'),


    # image
    path('image_add_subject/', views.image_add_subject, name='image_add_subject'),
    path('image_update_subject/', views.image_update_subject, name='image_update_subject'),
    path('image_delete_subject/', views.image_delete_subject, name='image_delete_subject'),
    # path('images_template_view/<int:template_id>/',views.images_template_view,name='images_template_view'),
    path('image_based_all/', views.image_based_all, name='image_based_all'),
    path('image_based_question_view/<int:id>', views.image_based_question_view, name='image_based_question_view'),
    path('image_based_question_add/<int:id>', views.image_based_question_add, name='image_based_question_add'),
    path('delete_image_question/', views.delete_image_question, name='delete_image_question'),


    # coding
    #  CODING EXAM QUESTION BANK
    path('coding_add_subject/', views.coding_add_subject, name='coding_add_subject'),
    path('coding_update_subject/', views.coding_update_subject, name='coding_update_subject'),
    path('coding_delete_subject/', views.coding_delete_subject, name='coding_delete_subject'),
    path('coding_add_category/', views.coding_add_category, name='coding_add_category'),
    path('coding_update_category/', views.coding_update_category, name='coding_update_category'),
    path('coding_delete_category/', views.coding_delete_category, name='coding_delete_category'),
    path('coding_subject_all/', views.coding_subject_all, name='coding_subject_all'),
    path('coding_category_all/<int:id>', views.coding_category_all, name='coding_category_all'),
    path('coding_question_add/<int:id>', views.coding_question_add, name='coding_question_add'),
    path('coding_question_view/<int:id>', views.coding_question_view, name='coding_question_view'),
    path('delete_coding_question/', views.delete_coding_question, name='delete_coding_question'),
    path('get_coding_question/',views.get_coding_question,name='get_coding_question'),
    path('update_coding_question/',views.update_coding_question,name='update_coding_question'),

    # descriptive

    path('descriptive_add_subject/', views.descriptive_add_subject, name='descriptive_add_subject'),
    path('descriptive_update_subject/', views.descriptive_update_subject, name='descriptive_update_subject'),
    path('descriptive_delete_subject/', views.descriptive_delete_subject, name='descriptive_delete_subject'),
    path('descriptive_list/', views.descriptive_list, name='descriptive_list'),
    path('descriptive_add/<int:id>', views.descriptive_add, name='descriptive_add'),
    path('descriptive_view/<int:id>', views.descriptive_view, name='descriptive_view'),
    path('delete_descriptive_question/', views.delete_descriptive_question, name='delete_descriptive_question'),
    path('get_descriptive_question/',views.get_descriptive_question,name='get_descriptive_question'),
    path('update_descriptive_question/',views.update_descriptive_question,name='update_descriptive_question'),


    # audio
    path('audio_add_subject/', views.audio_add_subject, name='audio_add_subject'),
    path('audio_update_subject/', views.audio_update_subject, name='audio_update_subject'),
    path('audio_delete_subject/', views.audio_delete_subject, name='audio_delete_subject'),
    # path('audio_template_view/<int:template_id>/',views.audio_template_view,name='audio_template_view'),
    path('audio_list/', views.audio_list, name='audio_list'),
    path('audio_add/<int:id>', views.audio_add, name='audio_add'),
    path('audio_view/<int:id>', views.audio_view, name='audio_view'),
    path('delete_audio_question/', views.delete_audio_question, name='delete_audio_question'),
    path('get_audio_question/',views.get_audio_question,name='get_audio_question'),
    path('update_audio_question/',views.update_audio_question,name='update_audio_question'),


    # template==========================================
    # Template Creation
    path('template_listing/', views.template_listing, name='template_listing'),
    path('add_category/', views.add_category, name='add_category'),
    path('delete_category/', views.delete_category, name='delete_category'),
    path('update_category/', views.update_category, name='update_category'),
    path('get_category/', views.get_category, name='get_category'),
    # path('create_template/', views.create_template, name='create_template'),
    path('delete_template/', views.delete_template, name='delete_template'),
    
    # Pre requisites
    path("pre_requisites/", views.pre_requisites, name="pre_requisites"),
    path("save_pre_requisites/", views.save_pre_requisites, name="save_pre_requisites"),
    path("view_pre_requisites/<int:id>", views.view_pre_requisites, name="view_pre_requisites"),
    path("prerequisites_edit/", views.pre_requisites_edit, name="pre_requisites_edit"),

    # mcq template
    path('add_exam_template/',views.add_exam_template,name='add_exam_template'),
    path('add_exam_template/<int:template_id>/',views.add_exam_template,name='add_exam_template'),
    path('exam_view/<int:pk>/',views.exam_view,name='exam_view'),
    path('exam_edit/<int:pk>/',views.exam_edit,name='exam_edit'),
    path('create_exam/<int:pk>',views.create_exam,name='create_exam'),
    path('mcq_total_questions/<int:id>', views.mcq_total_questions, name="mcq_total_questions"),
    path('mcq_template_view/<int:template_id>/',views.mcq_template_view, name='mcq_template_view'),


    # image template
    path('image_add_exam_template/',views.image_add_exam_template,name='image_add_exam_template'),
    path('image_add_exam_template/<int:template_id>',views.image_add_exam_template,name='image_add_exam_template'),
    path('image_exam_view/<int:pk>/',views.image_exam_view,name='image_exam_view'),
    path('image_create_exam/<int:pk>',views.image_create_exam,name='image_create_exam'),
    path('image_total_questions/<int:id>', views.image_total_questions, name="image_total_questions"),
    path('images_template_view/<int:template_id>/',views.images_template_view,name='images_template_view'),
    path('image_exam_edit/<int:pk>/',views.image_exam_edit,name='image_exam_edit'),

    # descriptive template
    path('descriptive_exam_template/',views.descriptive_exam_template,name='descriptive_exam_template'),
    path('descriptive_exam_view/<int:pk>/',views.descriptive_exam_view,name='descriptive_exam_view'),
    path('descriptive_exam_edit/<int:pk>/',views.descriptive_exam_edit,name='descriptive_exam_edit'),
    path('descriptive_create_exam/<int:pk>',views.descriptive_create_exam,name='descriptive_create_exam'),
    path('descriptive_get_count/',views.descriptive_get_count,name='get_count'),
    path('descriptive_template_view/<int:template_id>/',views.descriptive_template_view,name='descriptive_template_view'),
    path('descriptive_exam_template/<int:template_id>',views.descriptive_exam_template,name='descriptive_exam_template'),

    # audio/video template
    path('audio_exam_template/',views.audio_exam_template,name='audio_exam_template'),
    path('audio_exam_view/<int:pk>/',views.audio_exam_view,name='audio_exam_view'),
    path('audio_exam_edit/<int:pk>/',views.audio_exam_edit,name='audio_exam_edit'),
    path('audio_create_exam/<int:pk>',views.audio_create_exam,name='daudio_create_exam'),
    path('audio_get_count/',views.audio_get_count,name='audio_get_count'),
    path('audio_template_view/<int:template_id>/',views.audio_template_view,name='audio_template_view'),
    path('audio_exam_template/<int:template_id>',views.audio_exam_template,name='audio_exam_template'),

    # coding template
    path('coding_exam_configuration/', views.coding_exam_configuration, name='coding_exam_configuration'),
    path('coding_question_selection/', views.coding_question_selection, name='coding_question_selection'),
    path('coding_question_edit_selection/<int:template_id>', views.coding_question_edit_selection, name='coding_question_edit_selection'),
    path('coding_question_marking/', views.coding_question_marking, name='coding_question_marking'),
    path('coding_question_marking_edit/<int:exam_config_id>', views.coding_question_marking_edit, name='coding_question_marking_edit'),
    path('coding_question_rating/', views.coding_question_rating, name='coding_question_rating'),
    path('get_subject_categories/<int:subject_id>',views.get_subject_categories, name='get_subject_categories'),
    path('coding_template_view/<int:template_id>',views.coding_template_view,name="coding_template_view"),
    path('coding_question_rating_edit/<int:exam_config_id>', views.coding_question_rating_edit, name='coding_question_rating_edit'),
    path('coding_total_questions/<int:id>', views.coding_total_questions, name="coding_total_questions"),
    path('coding_exam_configuration/<int:template_id>', views.coding_exam_configuration, name='coding_exam_configuration'),

    # interview template
    path('interview_template/', views.interview_template, name='interview_template'),
    path('interview_template_edit/<int:interview_temp_id>', views.interview_template_edit,name='interview_template_edit'),
    path('interview_template_view/<int:interview_temp_id>', views.interview_template_view,name='interview_template_view'),

    # custom template
    path("custom_template/", views.custom_template, name="custom_template"),
    path("custom_stage/<int:id>", views.custom_stage, name="custom_stage"),
    
    
    
    # job template
    path('job_creation_template/', views.job_creation_template, name='job_creation_template'),
    path('job_creation_template_edit/<int:id>/', views.job_creation_template_edit, name='job_creation_template_edit'),
    path('get_job_template',views.get_job_template,name="get_job_template"),
    path('job_template_view/<int:template_id>/',views.job_template_view, name='job_template_view'),
    
    
    path('get_skills/',views.get_skills,name='get_skills'),


    # workflow
    path("workflow_list/", views.workflow_list, name="workflow_list"),
    path("create_workflow/", views.create_workflow, name="create_workflow"),
    path("edit_workflow/<int:id>", views.edit_workflow, name="edit_workflow"),
    path("workflow_configuration/", views.workflow_configuration, name="workflow_configuration"),
    path("workflow_configuration/<int:workflow_id>", views.workflow_configuration, name="workflow_configuration"),
    path("get_workflow_data/", views.get_workflow_data, name="get_workflow_data"),
    # path("workflow_selection/<int:id>", views.workflow_selection, name="workflow_selection"),
    path("workflow_view/<int:id>", views.workflow_view, name="workflow_view"),



    # jobcreation
    path('job_creation/', views.job_creation, name='job_creation'),
    path('job_template_creation/<int:jobtemplate_id>', views.job_template_creation, name='job_template_creation'),
    path('job_edit/<int:jobid>', views.job_creation, name='job_edit'),
    path('job_creation_select_template',views.job_creation_select_template,name='job_creation_select_template'),
    path('get_job_template',views.get_job_template,name="get_job_template"),
    path("created_job_view/<int:id>", views.created_job_view, name="created_job_view"),
    path("workflow_selection/<int:id>", views.workflow_selection, name="workflow_selection"),

    path('assign_job/',views.assign_job,name="assign_job"),
    path('unassign_recruiter/', views.unassign_recruiter, name='unassign_recruiter'),

    path("internal_submit_candidate/<int:id>", views.internal_submit_candidate, name="internal_submit_candidate"),

    path('job_applied_candidates_view/<int:id>', views.job_applied_candidates_view, name='job_applied_candidates_view'),

    path('job_close/<int:jobid>', views.job_close, name='job_close'),
    path('agency_portal_candidate_tablist/<int:candidate_id>/<int:job_id>',views.agency_portal_candidate_tablist,name='agency_portal_candidate_tablist'),


    path('coding_assessment/<int:id>',views.coding_assessment,name='coding_assessment'),

    path('get_job_stages/',views.get_job_stages,name='get_job_stages'),
    path('get_job_users/',views.get_job_users,name='get_job_users'),
    path('collaboration/',views.collaboration,name='collaboration'),


    path('descriptive_assessment',views.descriptive_assessment,name='descriptive_assessment'),
    path('audio_video_assessment',views.audio_video_assessment,name='audio_video_assessment'),
    # path('interview_assessment/<int:id>', views.interview_assessment, name='interview_assessment'),

    path("send_offer/<int:id>", views.send_offer, name="send_offer"),
    path("candidate_negotiate_offer/<int:id>", views.candidate_negotiate_offer, name="candidate_negotiate_offer"),


    path("notification_list/", views.notification_list, name="notification_list"),


    path("daily_submission/", views.daily_submission, name="daily_submission"),
    path('internal_candidate_basic_detail',views.internal_candidate_basic_detail,name="internal_candidate_basic_detail"),
    path("internal_redact_resume/<int:internal_candidate_id>/",views.internal_redact_resume,name="internal_redact_resume"),
    path("internal_save_redacted_resume/<int:internal_candidate_id>/",views.internal_save_redacted_resume,name="internal_save_redacted_resume"),
    path('get_job/',views.get_job,name="get_job"),
    path("submit_candidate_daily/<int:submitid>/",views.submit_candidate_daily,name="submit_candidate_daily"),
    path("applied_candidate_form/<int:int_cand_detail_id>/",views.applied_candidate_form,name="applied_candidate_form"),

    
]   