"""Контроллеры базы кандидатов и публичной формы отклика."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from apps.vacancies.models import Vacancy
from .forms import PublicApplicationForm
from .models import Candidate


@login_required
def candidate_list(request):
    qs = (
        Candidate.objects
        .select_related('source')
        .prefetch_related('resumes', 'applications__vacancy')
        .order_by('-created_at')
    )
    return render(request, 'candidates/candidate_list.html', {
        'candidates': qs,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Кандидаты', None)],
    })


@login_required
def candidate_detail(request, pk):
    candidate = get_object_or_404(
        Candidate.objects.prefetch_related('resumes', 'candidate_skills__skill',
                                            'applications__vacancy', 'applications__current_stage'),
        pk=pk,
    )
    return render(request, 'candidates/candidate_detail.html', {
        'candidate': candidate,
        'breadcrumbs': [('Дашборд', '/dashboard/'),
                         ('Кандидаты', '/candidates/'),
                         (candidate.full_name, None)],
    })


def apply_to_vacancy(request, slug):
    """Публичная форма отклика на вакансию (без авторизации)."""
    vacancy = get_object_or_404(Vacancy, slug=slug, status='published')

    if request.method == 'POST':
        form = PublicApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate, resume = form.save()
            # Создаём отклик. Скрининг запускается через сигнал в screening/signals.py
            from apps.pipeline.models import Application
            from apps.catalog.models import Stage
            stage_initial = (Stage.objects.filter(is_terminal=False).order_by('order').first())
            Application.objects.create(
                candidate=candidate,
                vacancy=vacancy,
                current_stage=stage_initial,
            )
            messages.success(request, 'Спасибо! Ваше резюме получено и обрабатывается системой. '
                                       'HR-менеджер свяжется с вами в течение 2 рабочих дней.')
            return redirect('vacancy_public', slug=vacancy.slug)
    else:
        form = PublicApplicationForm()
    return render(request, 'candidates/apply.html', {
        'form': form, 'vacancy': vacancy,
        'breadcrumbs': [('Главная', '/'), ('Вакансии', None),
                         (vacancy.title, f'/vacancies/public/{vacancy.slug}/'),
                         ('Отклик', None)],
    })
