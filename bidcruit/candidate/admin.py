from django.contrib import admin
from . import models
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy

admin.site.site_header = 'Bidcruit Administration'
admin.site.site_title = 'Bidcruit admin'
admin.site.register(models.PermissionsModel)
admin.site.register(models.Permissions)
admin.site.register(models.Month)
admin.site.register(models.Languages)
admin.site.register(models.Fluency)
admin.site.register(models.Country)
admin.site.register(models.State)
admin.site.register(models.City)
admin.site.register(models.Gender)
admin.site.register(models.MaritalType)
admin.site.register(models.Degree)
admin.site.register(models.UniversityBoard)
admin.site.register(models.Company)
admin.site.register(models.Tags)
admin.site.register(models.Skill)
admin.site.register(models.NoticePeriod)
admin.site.register(models.IndustryType)
admin.site.register(models.Source)
admin.site.register(models.PaymentTerms)
admin.site.register(models.ReplacementTerms)
admin.site.register(models.CandidateProfileTheme)
admin.site.register(models.RecruiterType)
admin.site.register(models.CompanyType)
admin.site.register(models.InternalCandidateAddedSkill)
admin.site.register(models.JobTypes)
admin.site.register(models.JobStatus)
admin.site.register(models.JobShift)
admin.site.register(models.QuestionDifficultyLevel)
admin.site.register(models.Stage_list)
admin.site.register(models.CodingApiSubjects)
admin.site.register(models.UploadCv)
admin.site.register(models.ThemeColor)
admin.site.register(models.ThemeFont)
admin.site.register(models.ThemeLayout)
admin.site.register(models.ThemeActive)
admin.site.register(models.ForgotPassword)
admin.site.register(models.Profile)
admin.site.register(models.CandidateProfile)
admin.site.register(models.CandidateSocialNetwork)
admin.site.register(models.CandidateEducation)
admin.site.register(models.CandidateExperience)
admin.site.register(models.CandidateCertificationAttachment)
admin.site.register(models.CandidateAward)
admin.site.register(models.CandidateSkillUserMap)
admin.site.register(models.CandidatePortfolio)
admin.site.register(models.CandidateSummary)
admin.site.register(models.CandidateOtherField)
admin.site.register(models.CandidateLanguage)
admin.site.register(models.CandidateHobbies)
admin.site.register(models.CandidateReference)
admin.site.register(models.Upload_Resume_Theme)
admin.site.register(models.CandidateJobPreference)
admin.site.register(models.CandidateJobPreferenceOther)
admin.site.register(models.ReferralDetails)
admin.site.register(models.Candidate_Hide_Fields)
admin.site.register(models.Gap)
admin.site.register(models.CandidateExpDocuments)
admin.site.register(models.CandidateSEO)
admin.site.register(models.CandidateCounter)
admin.site.register(models.candidate_job_apply_detail)
admin.site.register(models.company_data_request)
admin.site.register(models.JcrFill)
admin.site.register(models.JcrRatio)
admin.site.register(models.PreRequisitesFill)
admin.site.register(models.Mcq_Exam)
admin.site.register(models.Mcq_Exam_result)
admin.site.register(models.Descriptive_Exam)
admin.site.register(models.Descriptive_Exam_result)
admin.site.register(models.Image_Exam)
admin.site.register(models.Image_Exam_result)
admin.site.register(models.RandomMCQExam)
admin.site.register(models.RandomImageExam)
admin.site.register(models.AudioExamQuestionAttemptUnit)
admin.site.register(models.AudioExamAttempt)
admin.site.register(models.CodingScoreCardFill)
admin.site.register(models.CodingFrontEndExamFill)
admin.site.register(models.CodingBackEndExamFill)
admin.site.register(models.Coding_Exam_result)
admin.site.register(models.ExamTimeStatus)
admin.site.register(models.BasicDetail)
admin.site.register(models.FitScore)
admin.site.register(models.Agency_PreRequisitesFill)
admin.site.register(models.Agency_ExamTimeStatus)
admin.site.register(models.AgencyRandomMCQExam)
admin.site.register(models.AgencyRandomImageExam)
admin.site.register(models.Agency_Mcq_Exam)
admin.site.register(models.Agency_Mcq_Exam_result)
admin.site.register(models.Agency_Image_Exam)
admin.site.register(models.Agency_Image_Exam_result)
admin.site.register(models.AgencyDescriptive_Exam)
admin.site.register(models.AgencyDescriptive_Exam_result)
admin.site.register(models.AgencyAudioExamQuestionAttemptUnit)
admin.site.register(models.AgencyAudioExamAttempt)
admin.site.register(models.AgencyCodingScoreCardFill)
admin.site.register(models.AgencyCodingFrontEndExamFill)
admin.site.register(models.AgencyCodingBackEndExamFill)
admin.site.register(models.AgencyCoding_Exam_result)
admin.site.register(models.TastStatus)
admin.site.register(models.Priority)