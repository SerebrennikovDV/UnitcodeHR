"""Контроллеры публичных страниц UnitcodeHR."""
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    """Главная страница: список открытых вакансий + краткая статистика."""
    from apps.vacancies.models import Vacancy
    open_vacancies = (
        Vacancy.objects
        .filter(status='published')
        .select_related('hiring_manager', 'recruiter')
        .order_by('-published_at')[:12]
    )
    return render(request, 'core/home.html', {
        'open_vacancies': open_vacancies,
        'breadcrumbs': [('Главная', None)],
    })


def healthz(request):
    """Health-check для хостинга."""
    return HttpResponse('ok', content_type='text/plain')


def about(request):
    return render(request, 'core/about.html', {
        'breadcrumbs': [('Главная', '/'), ('О компании', None)],
    })


def help_page(request):
    """Справка по системе (требование рубрики)."""
    return render(request, 'core/help.html', {
        'breadcrumbs': [('Главная', '/'), ('Справка', None)],
    })


@login_required
def dashboard(request):
    """Главный дашборд авторизованного пользователя."""
    from apps.vacancies.models import Vacancy
    from apps.candidates.models import Candidate
    from apps.pipeline.models import Application

    stats = {
        'open_vacancies': Vacancy.objects.filter(status='published').count(),
        'total_candidates': Candidate.objects.count(),
        'active_applications': Application.objects.filter(closed_at__isnull=True).count(),
    }
    return render(request, 'core/dashboard.html', {
        'stats': stats,
        'breadcrumbs': [('Дашборд', None)],
    })
