# Тестовые данные

Загрузка фикстур происходит командами:

```bash
python main.py loaddata fixtures/01_roles.json
python main.py loaddata fixtures/02_departments.json
python main.py loaddata fixtures/03_positions.json
python main.py loaddata fixtures/04_sources.json
python main.py loaddata fixtures/05_stages.json
python main.py loaddata fixtures/06_skills.json
```

## Тестовые пользователи

Файл `07_demo_users.json` содержит шаблоны учётных записей, но без рабочих паролей
(хеши-заглушки). Для создания тестовых пользователей рекомендуется выполнить:

```bash
python main.py createsuperuser  # для администратора
python main.py shell <<'EOF'
from apps.accounts.models import User, Role
hr = User.objects.create_user(username='hr_lead', email='hr@unitcode.local',
                              password='HrUser#2026', first_name='Анна',
                              last_name='Иванова', is_staff=True,
                              role=Role.objects.get(code='hr'), department_id=5)
hm = User.objects.create_user(username='hire_lead', email='hire@unitcode.local',
                              password='Hire#2026', first_name='Михаил',
                              last_name='Лобов', is_staff=False,
                              role=Role.objects.get(code='hiring_manager'),
                              department_id=2)
EOF
```

## Тестовая вакансия со скиллами

```bash
python main.py shell <<'EOF'
from apps.vacancies.models import HiringRequest, Vacancy, VacancySkill
from apps.accounts.models import User
from apps.catalog.models import Skill

hm = User.objects.get(username='hire_lead')
hr = User.objects.get(username='hr_lead')

req = HiringRequest.objects.create(
    title='Middle Python Backend Developer',
    description='Развитие backend CRM-системы.',
    department_id=2, position_id=1, requested_by=hm,
    status='approved', salary_min=180000, salary_max=250000,
    urgency='high',
)
vac = Vacancy.objects.create(
    request=req, title='Middle Python Developer (Django)',
    description='Развитие backend CRM-системы на Django + PostgreSQL.',
    requirements='Опыт от 2 лет, уверенное знание Python, Django, PostgreSQL.',
    benefits='Удалённый формат, гибкий график, оплата самозанятому.',
    recruiter=hr, hiring_manager=hm,
    min_experience_years=2, status='published',
)
from django.utils import timezone
vac.published_at = timezone.now()
vac.save()

required = [(1, 1.5, True), (5, 1.5, True), (10, 1.2, True),
             (13, 1.0, False), (16, 1.0, False), (19, 0.8, False)]
for sid, w, req_flag in required:
    VacancySkill.objects.create(vacancy=vac, skill_id=sid, weight=w, is_required=req_flag)
print('OK:', vac.pk)
EOF
```
