

#------------------- means done
base_url = "http://192.168.1.148:8000/"

urls  = {}
#ALL IDS WILL BE DYNAMIC

#agency notifications

agency_invite_response = base_url + "agency/client_list/" #id will be provided later#------------------------

urls['agency_invite_response'] = agency_invite_response
#company notifications
agency_invite_url = base_url + "company/request_page/"#---------------------------
job_closed = base_url + "company/created_job_view/16" #id will be changed to dynamic id

agency_assign_user_for_job = base_url + "company/created_job_view/16" #id will be changed to dynamic id#TESTING  REQUIRED

notify_job_entities_when_hired ="" #possible in agency too
notify_for_evaluation = ""

#candidate_notifications
candidate_is_accepted = base_url+ "company/company_portal_candidate_tablist/84/16" 
applied_for_job = base_url+ "company/applied_candidates_view/14"  #-------------------------

workflow_created = ""
workflow_edited = ""
 


#GROUPABLE NOTIFICATIONS

template_changed = ""
job_opening_request = "" #to admin
job_opening_is_accepted = "" #to admin
# job_opening_is_rejected = "" #to admin #possible verb for filter

#chat messages 

mentioned_in_collaboration = ""