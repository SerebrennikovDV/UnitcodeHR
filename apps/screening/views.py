"""Контроллеры подсистемы скрининга."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Match
from .services import score_application, enrich_keywords_from_external


@login_required
def match_list(request):
    """Список всех скоров отсортирован по убыванию."""
    qs = (
        Match.objects
        .select_related('application__candidate', 'application__vacancy')
        .order_by('-score')[:200]
    )
    return render(request, 'screening/match_list.html', {
        'matches': qs,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Скрининг', None)],
    })


@login_required
def match_recalculate(request, pk):
    match = get_object_or_404(Match, pk=pk)
    score_application(match.application)
    messages.success(request, 'Скоринг пересчитан.')
    return redirect('application_detail', pk=match.application.pk)


@login_required
def enrich_keywords(request):
    """Запрос ключевых слов из внешних источников для конкретной вакансии."""
    query = request.GET.get('q', '').strip()
    keywords = []
    if query:
        keywords = enrich_keywords_from_external(query)
    return render(request, 'screening/enrich.html', {
        'query': query,
        'keywords': keywords,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Скрининг', '/screening/matches/'),
                         ('Обогащение ключей', None)],
    })
