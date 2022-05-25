from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from company.models import InterviewSchedule,CandidateJobStagesStatus,InterviewTemplate,InterviewScorecard,InterviewResult,InterviewScorecardResult
from django.http import HttpResponse, request
from django.contrib.auth import get_user_model
User = get_user_model()
# from videochat.models import PDF
# Create your views here.


@login_required(login_url="/")
def main_view(request,link):
    if InterviewSchedule.objects.filter(interview_link=link).exists():
        interview_obj = InterviewSchedule.objects.get(interview_link=link)
        interview_template = InterviewTemplate.objects.get(company_id=interview_obj.company_id,template=interview_obj.template)
        scorecards = InterviewScorecard.objects.filter(interview_template=interview_template)
        print('scorecards', scorecards)
        if request.user.is_candidate:
            if interview_obj.candidate_id.id != request.user.id:
                return HttpResponse('Invalid Link')
        if request.user.is_company:
            participants = []
            for participant in interview_obj.participants.all():
                participants.append(participant.id)
            if request.user.id not in participants:
                return HttpResponse('Invalid Link')
        context={}
        context['link'] = link
        context['jobid'] = interview_obj.job_id
        context['candidate_id'] = interview_obj.candidate_id.id
        context['scorecards'] = scorecards
        if request.method == 'POST':
            if request.is_ajax():
                interview_result, created = InterviewResult.objects.update_or_create(
                    candidate_id=interview_obj.candidate_id,
                    company_id=interview_obj.company_id,
                    user_id=User.objects.get(
                        id=request.user.id),
                    job_id=interview_obj.job_id,
                    interview_template=interview_template)
                for score in scorecards:
                    rating = request.POST.get('rating' + str(score.id))
                    comment = request.POST.get('comment' + str(score.id))
                    interview_result.scorecard_results.add(InterviewScorecardResult.objects.create(title=score.title,comment=comment,rating=rating))
                interview_obj.job_stages_id.assessment_done = True
                interview_obj.job_stages_id.save()
                return HttpResponse(True)
            if 'leave_interview' in request.POST:
                if request.user.is_candidate:
                    interview_obj.job_stages_id.status = 2
                    interview_obj.job_stages_id.save()
                    return redirect('candidate:applied_job_detail',interview_obj.job_id.id)
                if request.user.is_company:
                    return redirect('company:company_portal_candidate_tablist',candidate_id=interview_obj.candidate_id.id,job_id=interview_obj.job_id.id)
            if 'end_interview' in request.POST:
                interview_obj.is_completed = True
                interview_obj.save()
                interview_obj.job_stages_id.status = 2
                interview_obj.job_stages_id.save()
                if CandidateJobStagesStatus.objects.filter(company_id=interview_obj.company_id,
                                                           candidate_id=interview_obj.candidate_id,
                                                           job_id=interview_obj.job_id,
                                                           sequence_number=interview_obj.job_stages_id.sequence_number + 1).exists():
                    candidate_job_stage_obj = CandidateJobStagesStatus.objects.get(
                        company_id=interview_obj.company_id,
                        candidate_id=interview_obj.candidate_id,
                        job_id=interview_obj.job_id,
                        sequence_number=interview_obj.job_stages_id.sequence_number + 1)
                    candidate_job_stage_obj.status = 1
                    candidate_job_stage_obj.save()
                return redirect('company:company_portal_candidate_tablist',candidate_id=interview_obj.candidate_id.id,job_id=interview_obj.job_id.id)

        return render(request,"videochat/video_interview.html",context)
    else:
        return HttpResponse('Invalid Link')


# def draw(request):
#     pdf = PDF.objects.get(id=2)
#     # return render(request,"chat/drawing.html",{"pdf":pdf.pdf.url})
#     return render(request,"chat/test_draw.html",{"pdf":pdf.pdf.url})


def capture_image(request):
    return render(request,"videochat/capture_image.html")


def set_interview(request):
    return render(request,"videochat/set_interview.html")