"""Расчёт HR-метрик: time-to-hire, source-of-hire, конверсии воронки, cost-per-hire."""
from datetime import timedelta
from django.db.models import Avg, Count, F, ExpressionWrapper, DurationField, Q
from django.utils import timezone


def time_to_hire(period_days: int = 90) -> dict:
    """Среднее время от публикации до закрытия вакансии за период."""
    from apps.vacancies.models import Vacancy
    since = timezone.now() - timedelta(days=period_days)
    qs = Vacancy.objects.filter(
        status='closed', closed_at__gte=since,
        published_at__isnull=False,
    ).annotate(
        days=ExpressionWrapper(F('closed_at') - F('published_at'),
                                 output_field=DurationField())
    )
    aggregate = qs.aggregate(
        count=Count('id'),
        avg=Avg('days'),
    )
    avg_days = (aggregate['avg'].total_seconds() / 86400.0) if aggregate['avg'] else 0
    return {
        'period_days': period_days,
        'closed_count': aggregate['count'] or 0,
        'avg_days_to_hire': round(avg_days, 1),
    }


def source_of_hire() -> list[dict]:
    """Эффективность источников: число кандидатов, конверсия в найм."""
    from apps.catalog.models import Source
    rows = []
    for s in Source.objects.filter(is_active=True):
        total = s.candidates.count()
        hired = s.candidates.filter(applications__offer__hire__isnull=False).distinct().count()
        conversion = round((hired / total * 100), 2) if total else 0
        rows.append({
            'source': s.name,
            'total_candidates': total,
            'hired': hired,
            'conversion_pct': conversion,
            'cost_per_month': float(s.cost_per_month),
        })
    rows.sort(key=lambda r: -r['conversion_pct'])
    return rows


def funnel_conversions() -> list[dict]:
    """Конверсии по этапам воронки — сколько откликов достигло каждого этапа."""
    from apps.catalog.models import Stage
    from apps.pipeline.models import StageHistory
    result = []
    for s in Stage.objects.order_by('order'):
        reached = StageHistory.objects.filter(stage=s).values('application').distinct().count()
        result.append({
            'stage': s.name,
            'reached': reached,
            'color': s.color,
        })
    # Расчёт конверсии относительно первого этапа
    if result and result[0]['reached']:
        base = result[0]['reached']
        for r in result:
            r['conversion_pct'] = round(r['reached'] / base * 100, 1)
    return result


def cost_per_hire(period_days: int = 90) -> dict:
    """Стоимость найма за период (упрощённый расчёт: суммарная стоимость источников / число наймов)."""
    from apps.catalog.models import Source
    from apps.offers.models import Hire
    since = timezone.now() - timedelta(days=period_days)
    hires_count = Hire.objects.filter(created_at__gte=since).count()
    months = period_days / 30
    monthly_cost = sum(float(s.cost_per_month) for s in Source.objects.filter(is_active=True))
    total_cost = monthly_cost * months
    cph = round(total_cost / hires_count) if hires_count else 0
    return {
        'period_days': period_days,
        'hires': hires_count,
        'total_cost': round(total_cost),
        'cost_per_hire': cph,
    }


def probation_pass_rate(period_days: int = 180) -> dict:
    from apps.offers.models import Hire
    since = timezone.now() - timedelta(days=period_days)
    qs = Hire.objects.filter(probation_end__gte=since, probation_passed__isnull=False)
    total = qs.count()
    passed = qs.filter(probation_passed=True).count()
    rate = round((passed / total * 100), 1) if total else 0
    return {'period_days': period_days, 'total': total, 'passed': passed, 'rate': rate}
