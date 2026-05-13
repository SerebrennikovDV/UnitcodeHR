"""Контроллеры воронки подбора."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.catalog.models import Stage
from .models import Application, Interview, StageHistory


@login_required
def pipeline_board(request):
    """Канбан-доска воронки: колонки по этапам, отклики в виде карточек."""
    stages = Stage.objects.order_by('order')
    apps_by_stage = {}
    for s in stages:
        apps_by_stage[s.id] = (
            Application.objects
            .filter(current_stage=s, closed_at__isnull=True)
            .select_related('candidate', 'vacancy')
            .prefetch_related('candidate__screening_matches')[:50]
        )
    return render(request, 'pipeline/board.html', {
        'stages': stages,
        'apps_by_stage': apps_by_stage,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Воронка подбора', None)],
    })


@login_required
def application_detail(request, pk):
    application = get_object_or_404(
        Application.objects.select_related('candidate', 'vacancy', 'current_stage')
                            .prefetch_related('stage_history__stage', 'interviews'),
        pk=pk,
    )
    return render(request, 'pipeline/application_detail.html', {
        'application': application,
        'stages': Stage.objects.order_by('order'),
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Воронка подбора', '/pipeline/'),
                         (f'Отклик #{application.pk}', None)],
    })


@login_required
def application_move_stage(request, pk):
    if request.method != 'POST':
        return redirect('application_detail', pk=pk)
    application = get_object_or_404(Application, pk=pk)
    new_stage_id = request.POST.get('stage_id')
    comment = request.POST.get('comment', '').strip()
    rejection = request.POST.get('rejection_reason', '').strip()
    if new_stage_id:
        stage = get_object_or_404(Stage, pk=new_stage_id)
        application.current_stage = stage
        application.rejection_reason = rejection
        if stage.is_terminal:
            application.closed_at = timezone.now()
        application.save()
        # Сигнал в pipeline/signals.py создаст запись истории
        if comment:
            StageHistory.objects.filter(application=application).order_by('-changed_at').first().__class__.objects.create(
                application=application, stage=stage, changed_by=request.user, comment=comment,
            )
        messages.success(request, f'Кандидат перемещён на этап «{stage.name}».')
    return redirect('application_detail', pk=pk)


@login_required
def application_restore(request, pk):
    """Возвращает авто-отклонённого кандидата в воронку."""
    application = get_object_or_404(Application, pk=pk)
    initial_stage = Stage.objects.filter(is_terminal=False).order_by('order').first()
    application.current_stage = initial_stage
    application.closed_at = None
    application.rejection_reason = ''
    application.save()
    messages.success(request, f'Кандидат возвращён в воронку на этап «{initial_stage.name}».')
    return redirect('application_detail', pk=pk)


@login_required
def interview_schedule(request, app_pk):
    application = get_object_or_404(Application, pk=app_pk)
    if request.method == 'POST':
        Interview.objects.create(
            application=application,
            interviewer=request.user,
            kind=request.POST.get('kind', 'hr'),
            scheduled_at=request.POST.get('scheduled_at'),
            duration_minutes=int(request.POST.get('duration_minutes') or 60),
            meeting_link=request.POST.get('meeting_link', ''),
        )
        messages.success(request, 'Интервью запланировано.')
        return redirect('application_detail', pk=application.pk)
    return render(request, 'pipeline/interview_form.html', {
        'application': application,
        'breadcrumbs': [('Дашборд', '/dashboard/'),
                         ('Воронка подбора', '/pipeline/'),
                         (f'Отклик #{application.pk}', f'/pipeline/applications/{application.pk}/'),
                         ('Запланировать интервью', None)],
    })
