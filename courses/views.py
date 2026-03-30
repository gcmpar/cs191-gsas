from django.shortcuts import render, get_object_or_404, redirect
from .models import Course
from .forms import CourseForm


def courses_search(request):
    courses = Course.objects.select_related('program__school').all()
    return render(request, 'courses/search.html', {
        'courses': courses,
    })


def course_view(request, course_id):
    course = get_object_or_404(
        Course.objects.select_related('program__school'),
        pk=course_id
    )
    return render(request, 'courses/view.html', {
        'course': course,
    })


def course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect('courses:view', course_id=course.course_id)
    else:
        form = CourseForm()
    return render(request, 'courses/add.html', {
        'form': form,
    })


def course_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:view', course_id=course_id)
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/edit.html', {
        'course': course,
        'form':   form,
    })


def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('courses:search')
    return redirect('courses:edit', course_id=course_id)