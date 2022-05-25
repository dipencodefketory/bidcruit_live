from django.shortcuts import render

def term_and_condition(request):
    return render(request,'accounts/term-and-condition.html')

def privacy_policy(request):
    return render(request,'accounts/privacy-policy.html')