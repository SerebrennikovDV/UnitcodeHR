"""Расчёт скора соответствия резюме требованиям вакансии."""
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class ScoringResult:
    """Результат расчёта скора с разложением по составляющим."""
    score: Decimal = Decimal('0')
    verdict: str = 'auto_rejected'
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    experience_match: bool = False
    extracted_experience_years: float | None = None
    reasons: list[str] = field(default_factory=list)


def calculate_score(
    *,
    resume_text: str,
    required_keywords: list[tuple[str, float, bool]],
    min_experience_years: int,
    extracted_experience_years: float | None,
    auto_reject_threshold: float = 50.0,
    recommend_threshold: float = 70.0,
) -> ScoringResult:
    """Рассчитывает интегральный показатель соответствия.

    Логика:
        1. Скор по ключевым словам — взвешенная сумма найденных тегов,
           нормированная на максимально возможный вес. Обязательные ключевые
           слова считаются с двойным весом.
        2. Бонус за соответствие требованию по опыту работы:
           если extracted_experience_years ≥ min_experience_years, добавляется
           до 15 пунктов; иначе из итогового скора вычитается штраф.
        3. Итоговый скор обрезается в диапазоне [0, 100] и сравнивается с
           порогами для вердикта.

    Параметры:
        resume_text: лемматизированный текст резюме.
        required_keywords: список троек (лемма, вес, обязательное).
        min_experience_years: требуемый опыт работы.
        extracted_experience_years: фактический опыт из резюме (или None).
    """
    result = ScoringResult(extracted_experience_years=extracted_experience_years)
    if not resume_text:
        result.reasons.append('Не удалось извлечь текст из резюме')
        return result

    lowered = resume_text.lower()

    # 1) Соответствие по ключевым словам
    total_weight = 0.0
    matched_weight = 0.0
    for term, weight, is_required in required_keywords:
        effective_weight = weight * (2.0 if is_required else 1.0)
        total_weight += effective_weight
        if term.lower() in lowered:
            matched_weight += effective_weight
            result.matched_keywords.append(term)
        else:
            result.missing_keywords.append(term)

    if total_weight == 0:
        keyword_score = 0.0
        result.reasons.append('Для вакансии не задан перечень ключевых требований')
    else:
        keyword_score = (matched_weight / total_weight) * 100.0

    # 2) Учёт опыта работы
    exp_bonus = 0.0
    if min_experience_years <= 0:
        result.experience_match = True
        result.reasons.append('Опыт работы для вакансии не регламентирован')
    elif extracted_experience_years is None:
        result.experience_match = False
        exp_bonus = -5.0
        result.reasons.append('Не удалось извлечь опыт работы из резюме')
    elif extracted_experience_years >= min_experience_years:
        result.experience_match = True
        # бонус прямо пропорционален «запасу» по опыту
        surplus = extracted_experience_years - min_experience_years
        exp_bonus = min(15.0, 5.0 + surplus * 1.5)
        result.reasons.append(
            f'Опыт работы {extracted_experience_years:.0f} лет ≥ требуемых '
            f'{min_experience_years} лет (+{exp_bonus:.1f} б.)'
        )
    else:
        result.experience_match = False
        gap = min_experience_years - extracted_experience_years
        exp_bonus = -min(20.0, 5.0 + gap * 3.0)
        result.reasons.append(
            f'Опыт работы {extracted_experience_years:.0f} лет меньше требуемых '
            f'{min_experience_years} лет ({exp_bonus:.1f} б.)'
        )

    final_score = max(0.0, min(100.0, keyword_score + exp_bonus))
    result.score = Decimal(f'{final_score:.2f}')

    if final_score >= recommend_threshold:
        result.verdict = 'recommended'
    elif final_score >= auto_reject_threshold:
        result.verdict = 'match'
    else:
        result.verdict = 'auto_rejected'

    if result.matched_keywords:
        result.reasons.insert(0,
            f'Найдены ключевые слова: {", ".join(result.matched_keywords[:10])}')
    if result.missing_keywords:
        result.reasons.append(
            f'Не найдены: {", ".join(result.missing_keywords[:10])}')

    return result
