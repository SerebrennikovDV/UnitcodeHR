"""Команда заполнения БД демонстрационными данными для проверки и скриншотов.

Использование:
    python manage.py seed_demo                 # обычный запуск
    python manage.py seed_demo --reset         # удалить старые демо-данные перед заполнением
"""
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.candidates.models import Candidate, CandidateSkill, Resume
from apps.catalog.models import Skill, Stage
from apps.pipeline.models import Application
from apps.vacancies.models import HiringRequest, Vacancy, VacancySkill


VACANCY_SKILLS = [
    ('Python', Decimal('1.5'), True),
    ('Django', Decimal('1.5'), True),
    ('PostgreSQL', Decimal('1.2'), True),
    ('Docker', Decimal('1.0'), False),
    ('REST API', Decimal('1.0'), False),
    ('pytest', Decimal('0.8'), False),
]

CANDIDATES = [
    {
        'first_name': 'Алексей',
        'last_name': 'Петров',
        'email': 'alexey.petrov@example.com',
        'phone': '+7 (999) 111-22-33',
        'expected_salary': Decimal('230000'),
        'skill_levels': {'Python': 5, 'Django': 5, 'PostgreSQL': 4, 'Docker': 4, 'REST API': 5, 'pytest': 4},
        'resume_text': (
            'Алексей Петров — Backend-разработчик\n\n'
            'Опыт работы: 5 лет.\n\n'
            'Профессиональные навыки: Python (5 лет), Django REST Framework, PostgreSQL, '
            'Docker и docker-compose, REST API design, pytest, Celery, Redis, Linux, Git, '
            'CI/CD через GitHub Actions.\n\n'
            'Опыт работы:\n'
            '2020-2025 — ООО «WebDev» — Backend-разработчик. Разрабатывал высоконагруженные '
            'сервисы на Django и FastAPI. Покрывал код тестами через pytest. Деплоил в Docker.\n'
            '2019-2020 — стажёр Python-разработчика.'
        ),
    },
    {
        'first_name': 'Мария',
        'last_name': 'Сидорова',
        'email': 'maria.sidorova@example.com',
        'phone': '+7 (999) 222-33-44',
        'expected_salary': Decimal('200000'),
        'skill_levels': {'Python': 4, 'Django': 4, 'PostgreSQL': 3, 'Docker': 3},
        'resume_text': (
            'Сидорова Мария Александровна — Python-разработчик\n\n'
            'Опыт работы 3 года.\n\n'
            'Стек: Python 3, Django, PostgreSQL, Docker, Git, REST. '
            'Английский B2.\n\n'
            '2022-2025 — ООО «Старт-ап» — Python-разработчик. '
            'Развитие CRM-системы на Django, миграции PostgreSQL, '
            'контейнеризация через Docker.'
        ),
    },
    {
        'first_name': 'Дмитрий',
        'last_name': 'Кузнецов',
        'email': 'dmitry.kuznetsov@example.com',
        'phone': '+7 (999) 333-44-55',
        'expected_salary': Decimal('180000'),
        'skill_levels': {'Python': 3, 'Django': 3, 'PostgreSQL': 2},
        'resume_text': (
            'Кузнецов Дмитрий — Junior Python-разработчик\n\n'
            'Опыт работы 2 года.\n\n'
            'Навыки: Python, Django, PostgreSQL базовый, Git, Linux.\n\n'
            '2023-2025 — ИП «Иванов» — Junior-разработчик. '
            'Участвовал в разработке внутренних инструментов на Django.'
        ),
    },
    {
        'first_name': 'Виктория',
        'last_name': 'Морозова',
        'email': 'victoria.morozova@example.com',
        'phone': '+7 (999) 444-55-66',
        'expected_salary': Decimal('150000'),
        'skill_levels': {'JavaScript': 4, 'TypeScript': 3, 'React': 4, 'Vue': 2},
        'resume_text': (
            'Морозова Виктория — Frontend-разработчик\n\n'
            'Опыт работы 2 года.\n\n'
            'Навыки: JavaScript, TypeScript, React, Vue, HTML5, CSS3, Bootstrap.\n\n'
            '2023-2025 — ООО «Studio» — Frontend-разработчик. '
            'Вёрстка интерфейсов на React.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Заполняет БД демонстрационными данными для проверки и скриншотов.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true',
                              help='Удалить старые демо-данные перед заполнением.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        hr, hm = self._ensure_users()
        vacancy = self._ensure_vacancy(hr, hm)
        applications = self._ensure_applications(vacancy)
        self._print_summary(applications)

    def _reset(self):
        """Удаляет ранее созданные демо-данные (по email-маркерам)."""
        Candidate.objects.filter(email__endswith='@example.com').delete()
        Vacancy.objects.filter(title__icontains='Middle Python Developer').delete()
        HiringRequest.objects.filter(title__icontains='Middle Python Backend').delete()
        User.objects.filter(username__in=['hr_lead', 'hire_lead']).delete()
        self.stdout.write(self.style.WARNING('Старые демо-данные удалены.'))

    def _ensure_users(self) -> tuple[User, User]:
        hr_role = Role.objects.get(code=Role.CODE_HR)
        hm_role = Role.objects.get(code=Role.CODE_HIRING_MANAGER)

        hr, created_hr = User.objects.get_or_create(
            username='hr_lead',
            defaults={
                'email': 'hr@unitcode.local', 'first_name': 'Анна', 'last_name': 'Иванова',
                'is_staff': True, 'role': hr_role, 'department_id': 5,
            },
        )
        if created_hr:
            hr.set_password('HrUser2026')
            hr.save()
            self.stdout.write(self.style.SUCCESS(f'Создан HR-пользователь {hr.username} (пароль HrUser2026).'))

        hm, created_hm = User.objects.get_or_create(
            username='hire_lead',
            defaults={
                'email': 'hire@unitcode.local', 'first_name': 'Михаил', 'last_name': 'Лобов',
                'is_staff': False, 'role': hm_role, 'department_id': 2,
            },
        )
        if created_hm:
            hm.set_password('Hire2026')
            hm.save()
            self.stdout.write(self.style.SUCCESS(f'Создан Hiring Manager {hm.username} (пароль Hire2026).'))
        return hr, hm

    def _ensure_vacancy(self, hr: User, hm: User) -> Vacancy:
        req, created = HiringRequest.objects.get_or_create(
            title='Middle Python Backend Developer',
            defaults={
                'description': 'Развитие backend CRM-системы UnitcodeHR.',
                'department_id': 2, 'position_id': 1, 'requested_by': hm,
                'status': HiringRequest.STATUS_APPROVED,
                'salary_min': Decimal('180000'), 'salary_max': Decimal('250000'),
                'urgency': 'high',
            },
        )

        vacancy, created_v = Vacancy.objects.get_or_create(
            title='Middle Python Developer (Django)',
            defaults={
                'request': req,
                'description': 'Развитие backend CRM-системы на Django + PostgreSQL.',
                'requirements': 'Опыт от 2 лет, уверенное знание Python, Django, PostgreSQL. '
                                  'Будет плюсом: Docker, REST API, pytest.',
                'benefits': 'Удалённый формат, гибкий график, оплата самозанятому или ИП.',
                'recruiter': hr, 'hiring_manager': hm,
                'min_experience_years': 2,
                'status': Vacancy.STATUS_PUBLISHED,
                'published_at': timezone.now(),
            },
        )
        if created_v:
            self.stdout.write(self.style.SUCCESS(f'Создана вакансия #{vacancy.pk} — {vacancy.title}'))

        for skill_name, weight, required in VACANCY_SKILLS:
            skill = Skill.objects.get(name=skill_name)
            VacancySkill.objects.get_or_create(
                vacancy=vacancy, skill=skill,
                defaults={'weight': weight, 'is_required': required},
            )
        return vacancy

    def _ensure_applications(self, vacancy: Vacancy) -> list[Application]:
        new_stage = Stage.objects.get(name='Новый отклик')
        media_root = Path(settings.MEDIA_ROOT)
        media_root.mkdir(parents=True, exist_ok=True)
        results = []
        for payload in CANDIDATES:
            candidate, created = Candidate.objects.get_or_create(
                email=payload['email'],
                defaults={
                    'first_name': payload['first_name'], 'last_name': payload['last_name'],
                    'phone': payload['phone'], 'expected_salary': payload['expected_salary'],
                    'source_id': 1,
                },
            )
            for skill_name, level in payload['skill_levels'].items():
                skill = Skill.objects.get(name=skill_name)
                CandidateSkill.objects.get_or_create(
                    candidate=candidate, skill=skill,
                    defaults={'level': level},
                )

            resume = candidate.resumes.filter(is_primary=True).first()
            if not resume:
                resume = Resume(candidate=candidate, is_primary=True,
                                  original_filename=f'{candidate.last_name}_resume.txt')
                resume.file.save(
                    f'{candidate.last_name.lower()}_resume.txt',
                    ContentFile(payload['resume_text'].encode('utf-8')),
                    save=False,
                )
                resume.file_size = len(payload['resume_text'].encode('utf-8'))
                resume.save()
                if created:
                    self.stdout.write(f'  + Резюме для {candidate} ({resume.file_size} байт)')

            application, app_created = Application.objects.get_or_create(
                candidate=candidate, vacancy=vacancy,
                defaults={
                    'current_stage': new_stage,
                    'cover_letter': f'Здравствуйте! Хочу присоединиться к команде {vacancy.title}.',
                },
            )
            if app_created:
                self.stdout.write(self.style.SUCCESS(
                    f'Создан отклик #{application.pk}: {candidate} -> {vacancy.title}'
                ))
            results.append(application)
        return results

    def _print_summary(self, applications: list[Application]):
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Сводка по откликам ==='))
        for app in applications:
            match = getattr(app, 'match', None)
            if match:
                self.stdout.write(
                    f'  #{app.pk} {app.candidate} — score {match.score}%, verdict={match.verdict}'
                )
            else:
                self.stdout.write(f'  #{app.pk} {app.candidate} — match ещё не посчитан')
