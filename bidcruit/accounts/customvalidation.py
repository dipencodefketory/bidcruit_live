import re
from django.http import HttpResponse
def password_validate(request):

    password = request.POST.get("password")

    atLeastTenCharacters = ".{6,}"
    hasAtLeastTenCharacters = re.findall(atLeastTenCharacters, password)
    if (not hasAtLeastTenCharacters):
        return HttpResponse("Password should be at least 6 characters long!")

    atLeastOneDigit = "[0-9]"
    hasAtLeastOneDigit = re.findall(atLeastOneDigit, password)
    if (not hasAtLeastOneDigit):
        return HttpResponse("Password should have at least one digit!")

    atLeastOneLower = "[a-z]"
    hasAtLeastOneLower = re.findall(atLeastOneLower, password)
    if (not hasAtLeastOneLower):
        return HttpResponse("Password should have at least one lower case character!")

    specialCharacters = "[@$&*_#]"
    hasSpecialCharacters = re.findall(specialCharacters, password)
    if (not hasSpecialCharacters):
        return HttpResponse("Password should NOT have special characters!")

    if (hasAtLeastTenCharacters and hasAtLeastOneDigit and hasAtLeastOneUpper and hasAtLeastOneLower and hasSpecialCharacters):
        return HttpResponse("Valid password")
    else:
        return HttpResponse("Password not valid")

def match_password(request):
    password = request.POST.get("password")
    cpassword = request.POST.get("cpassword")
    if password==cpassword:
        return HttpResponse("Password Match")
    else:
        return HttpResponse("Password dose not match")