from django.shortcuts import render
from django.http import HttpResponse

def applicants_search(request):
    # TODO
    return render(request, 'applicants/search.html')

def applicant_view(request, applicant_id):
    # TODO
    return render(request, 'applicants/view.html')

def applicant_edit(request, applicant_id):
    # TODO
    return HttpResponse("")