"""Контроллеры вакансий и заявок на найм."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import HiringRequest, Vacancy
from .forms import HiringRequestForm


@login_required
def vacancy_list(request):
    qs = Vacancy.objects.filter(status__in=['draft', 'published']).order_by('-published_at')
    return render(request, 'vacancies/vacancy_list.html', {
        'vacancies': qs,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Вакансии', None)],
    })


@login_required
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    return render(request, 'vacancies/vacancy_detail.html', {
        'vacancy': vacancy,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Вакансии', '/vacancies/'),
                         (vacancy.title, None)],
    })


def vacancy_public_detail(request, slug):
    """Публичная страница вакансии без авторизации."""
    vacancy = get_object_or_404(Vacancy, slug=slug, status='published')
    return render(request, 'vacancies/vacancy_public.html', {
        'vacancy': vacancy,
        'breadcrumbs': [('Главная', '/'), ('Вакансии', None), (vacancy.title, None)],
    })


@login_required
def hiring_request_list(request):
    if request.user.is_hr or request.user.is_administrator:
        qs = HiringRequest.objects.all()
    else:
        qs = HiringRequest.objects.filter(requested_by=request.user)
    qs = qs.select_related('department', 'position', 'requested_by')
    return render(request, 'vacancies/hiring_request_list.html', {
        'requests': qs,
        'breadcrumbs': [('Дашборд', '/dashboard/'),
                         ('Заявки на найм', None)],
    })


@login_required
def hiring_request_create(request):
    if request.method == 'POST':
        form = HiringRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.requested_by = request.user
            obj.status = HiringRequest.STATUS_PENDING
            obj.save()
            messages.success(request, 'Заявка отправлена на согласование.')
            return redirect('hiring_request_detail', pk=obj.pk)
    else:
        form = HiringRequestForm()
    return render(request, 'vacancies/hiring_request_form.html', {
        'form': form,
        'breadcrumbs': [('Дашборд', '/dashboard/'),
                         ('Заявки на найм', '/vacancies/requests/'),
                         ('Новая заявка', None)],
    })


@login_required
def hiring_request_detail(request, pk):
    obj = get_object_or_404(HiringRequest, pk=pk)
    return render(request, 'vacancies/hiring_request_detail.html', {
        'request_obj': obj,
        'breadcrumbs': [('Дашборд', '/dashboard/'),
                         ('Заявки на найм', '/vacancies/requests/'),
                         (f'Заявка #{obj.pk}', None)],
    })
