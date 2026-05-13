"""Сервисный слой подсистемы скрининга — оркестрация парсинга и скоринга."""
import logging
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from .lemmatizer import lemmatize_text, lemmatize_keywords
from .models import Match, ResumeParse
from .parser import extract_text, extract_experience_years
from .scorer import calculate_score

logger = logging.getLogger(__name__)


def parse_resume(resume) -> ResumeParse:
    """Парсит файл резюме и сохраняет результат в БД."""
    raw_text = extract_text(resume.file.path)
    normalized = lemmatize_text(raw_text)
    years = extract_experience_years(raw_text)

    parsed, _ = ResumeParse.objects.update_or_create(
        resume=resume,
        defaults={
            'raw_text': raw_text[:50_000],  # ограничение по размеру
            'normalized_text': normalized[:50_000],
            'years_experience': Decimal(f'{years:.1f}') if years else None,
            'parser_version': settings.SCREENING['PARSER_VERSION'],
        },
    )
    logger.info('Резюме %s обработано (опыт: %s лет)', resume.pk, years)
    return parsed


def score_application(application) -> Match:
    """Считает скор соответствия резюме кандидата требованиям вакансии."""
    vacancy = application.vacancy
    candidate = application.candidate
    resume = candidate.resumes.filter(is_primary=True).first() or candidate.resumes.first()
    if not resume:
        logger.warning('У кандидата %s нет резюме — скрининг невозможен', candidate.pk)
        return _create_empty_match(application, reason='Не приложено резюме')

    parsed = getattr(resume, 'parsed', None) or parse_resume(resume)

    # Список требований: (лемма, вес, обязательно)
    required = []
    for vs in vacancy.vacancy_skills.select_related('skill').all():
        terms = [vs.skill.lemma or vs.skill.name] + list(vs.skill.aliases or [])
        for term in terms:
            required.append((lemmatize_keywords([term])[0],
                              float(vs.weight), vs.is_required))

    result = calculate_score(
        resume_text=parsed.normalized_text,
        required_keywords=required,
        min_experience_years=vacancy.min_experience_years,
        extracted_experience_years=float(parsed.years_experience) if parsed.years_experience else None,
        auto_reject_threshold=float(settings.SCREENING['AUTO_REJECT_THRESHOLD']),
        recommend_threshold=float(settings.SCREENING['RECOMMEND_THRESHOLD']),
    )

    match, _ = Match.objects.update_or_create(
        application=application,
        defaults={
            'score': result.score,
            'verdict': result.verdict,
            'matched_keywords': result.matched_keywords,
            'missing_keywords': result.missing_keywords,
            'experience_match': result.experience_match,
            'extracted_experience_years': (
                Decimal(f'{result.extracted_experience_years:.1f}')
                if result.extracted_experience_years else None
            ),
            'reasons': '\n'.join(result.reasons),
            'candidate': candidate,
        },
    )

    # Авто-отклонение
    if result.verdict == 'auto_rejected':
        _apply_auto_rejection(application)
    logger.info('Скоринг %s завершён: %s %% (%s)',
                application.pk, result.score, result.verdict)
    return match


def _create_empty_match(application, *, reason: str) -> Match:
    match, _ = Match.objects.update_or_create(
        application=application,
        defaults={
            'score': Decimal('0'),
            'verdict': 'auto_rejected',
            'matched_keywords': [],
            'missing_keywords': [],
            'experience_match': False,
            'reasons': reason,
            'candidate': application.candidate,
        },
    )
    return match


def _apply_auto_rejection(application) -> None:
    """Переводит отклик в этап «Отклонено системой»."""
    from apps.catalog.models import Stage
    stage = Stage.objects.filter(is_terminal=True, name__icontains='систем').first()
    if not stage:
        stage = Stage.objects.filter(is_terminal=True).order_by('order').first()
    if stage:
        application.current_stage = stage
        application.closed_at = timezone.now()
        application.rejection_reason = 'Авто-отклонено системой (score < 50%)'
        application.save(update_fields=['current_stage', 'closed_at', 'rejection_reason'])


def schedule_screening(application) -> None:
    """Точка входа из сигнала post_save Application — запускает скоринг.

    В простой версии — синхронно, без очередей. В production-режиме можно
    обернуть в Celery-задачу score_application.delay(application.pk).
    """
    try:
        score_application(application)
    except Exception as exc:
        logger.exception('Скрининг отклика %s провален: %s', application.pk, exc)


def enrich_keywords_from_external(query: str, sources: list[str] | None = None) -> list[str]:
    """Запрашивает у внешних коннекторов список ключевых слов по похожим вакансиям."""
    from connectors import get_connector
    sources = sources or ['hh', 'superjob', 'avito']
    bag: dict[str, int] = {}
    for src in sources:
        try:
            connector = get_connector(src)
            for vac in connector.search(query, limit=20):
                for kw in vac.get('keywords', []):
                    bag[kw.lower()] = bag.get(kw.lower(), 0) + 1
        except Exception as exc:
            logger.warning('Источник %s недоступен: %s', src, exc)
    # Возвращаем топ-30 по частоте
    return [k for k, _ in sorted(bag.items(), key=lambda x: -x[1])[:30]]
