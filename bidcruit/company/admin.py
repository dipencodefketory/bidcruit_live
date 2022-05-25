from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Company)
admin.site.register(models.Role)
admin.site.register(models.RolePermissions)
admin.site.register(models.CandidateHire)
admin.site.register(models.CandidateSelectedPreference)
admin.site.register(models.CompanyProfile)
admin.site.register(models.ShortlistedCandidates)
admin.site.register(models.InternalCandidate)
admin.site.register(models.InternalCandidateProfessionalDetail)
admin.site.register(models.InternalCandidateEducation)
admin.site.register(models.InternalCandidateExperience)
admin.site.register(models.InternalCandidatePreference)
admin.site.register(models.InternalCandidatePortfolio)
admin.site.register(models.InternalCandidateSource)
admin.site.register(models.InternalCandidateAttachment)
admin.site.register(models.InternalCandidateProfessionalSkill)
admin.site.register(models.Department)
admin.site.register(models.JobCreation)
admin.site.register(models.CompanyAssignJob)
admin.site.register(models.AssignExternal)
admin.site.register(models.AssignInternal)
admin.site.register(models.CompanyJobShift)
admin.site.register(models.TemplateCategory)
admin.site.register(models.Template_creation)
admin.site.register(models.JCR)
admin.site.register(models.PreRequisites)
admin.site.register(models.Workflows)
admin.site.register(models.WorkflowStages)
admin.site.register(models.WorkflowConfiguration)
admin.site.register(models.JobCreationTemplate)
admin.site.register(models.JobWorkflow)
admin.site.register(models.AppliedCandidate)
admin.site.register(models.Paragraph_subject)
admin.site.register(models.Paragraph)
admin.site.register(models.Paragraph_option)
admin.site.register(models.Descriptive_subject)
admin.site.register(models.Descriptive)
admin.site.register(models.MCQ_subject)
admin.site.register(models.mcq_Question)
admin.site.register(models.ExamTemplate)
admin.site.register(models.ExamQuestionUnit)
admin.site.register(models.QuestionPaper)
admin.site.register(models.ImageSubject)
admin.site.register(models.ImageQuestion)
admin.site.register(models.ImageOption)
admin.site.register(models.CodingSubject)
admin.site.register(models.CodingSubjectCategory)
admin.site.register(models.CodingQuestion)
admin.site.register(models.CodingExamConfiguration)
admin.site.register(models.CodingExamQuestions)
admin.site.register(models.CodingScoreCard)
admin.site.register(models.DescriptiveExamTemplate)
admin.site.register(models.DescriptiveExamQuestionUnit)
admin.site.register(models.DescriptiveQuestionPaper)
admin.site.register(models.ImageExamTemplate)
admin.site.register(models.ImageExamQuestionUnit)
admin.site.register(models.ImageQuestionPaper)
admin.site.register(models.Audio_subject)
admin.site.register(models.Audio)
admin.site.register(models.AudioExamTemplate)
admin.site.register(models.AudioExamQuestionUnit)
admin.site.register(models.AudioQuestionPaper)
admin.site.register(models.CandidateJobStagesStatus)
admin.site.register(models.Collaboration)
admin.site.register(models.Employee)
admin.site.register(models.AssociateCandidateAgency)
admin.site.register(models.CandidateTempDatabase)
admin.site.register(models.CandidateCategories)
admin.site.register(models.Tags)
admin.site.register(models.InternalCandidateBasicDetails)
admin.site.register(models.InternalCandidateNotes)
admin.site.register(models.AssociateCandidateInternal)
admin.site.register(models.InterviewTemplate)
admin.site.register(models.InterviewScorecard)
admin.site.register(models.InterviewSchedule)
admin.site.register(models.OfferNegotiation)
admin.site.register(models.JobOffer)
admin.site.register(models.CandidateJobStatus)
admin.site.register(models.InterviewScorecardResult)
admin.site.register(models.InterviewResult)
admin.site.register(models.OnTheGoStages)
admin.site.register(models.CustomTemplateScorecard)
admin.site.register(models.CustomTemplate)
admin.site.register(models.CustomScorecardResult)
admin.site.register(models.CustomResult)
admin.site.register(models.Tracker)
admin.site.register(models.DailySubmission)
admin.site.register(models.TaskCategories)
admin.site.register(models.TaskManagment)