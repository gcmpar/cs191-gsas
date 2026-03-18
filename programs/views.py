from django.shortcuts import render, get_object_or_404, redirect
from academics.models import Program
from .forms import ProgramForm


def programs_search(request):
    programs = Program.objects.select_related('school').all()
    return render(request, 'programs/search.html', {
        'programs': programs,
    })


def program_view(request, program_id):
    program = get_object_or_404(Program.objects.select_related('school'), pk=program_id)
    return render(request, 'programs/view.html', {
        'program': program,
    })


def program_add(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            return redirect('programs:view', program_id=program.program_id)
    else:
        form = ProgramForm()
    return render(request, 'programs/add.html', {
        'form': form,
    })


def program_edit(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect('programs:view', program_id=program_id)
    else:
        form = ProgramForm(instance=program)
    return render(request, 'programs/edit.html', {
        'program': program,
        'form':    form,
    })


def program_delete(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    if request.method == 'POST':
        program.delete()
        return redirect('programs:search')
    return redirect('programs:edit', program_id=program_id)