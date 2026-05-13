from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Skill, Department


@login_required
def skill_list(request):
    skills = Skill.objects.filter(is_active=True).order_by('category', 'name')
    return render(request, 'catalog/skill_list.html', {
        'skills': skills,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Справочники', None),
                         ('Навыки', None)],
    })


@login_required
def department_list(request):
    departments = Department.objects.filter(is_active=True).order_by('name')
    return render(request, 'catalog/department_list.html', {
        'departments': departments,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Справочники', None),
                         ('Подразделения', None)],
    })
