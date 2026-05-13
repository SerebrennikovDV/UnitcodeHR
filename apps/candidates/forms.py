"""Формы публичного отклика и редактирования кандидата."""
from django import forms

from .models import Candidate, Resume


class PublicApplicationForm(forms.Form):
    """Форма отклика на вакансию с публичной страницы."""
    first_name = forms.CharField(label='Имя', max_length=150,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Фамилия', max_length=150,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='E-mail',
                              widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label='Телефон', max_length=20, required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': '+7 (___) ___-__-__'}))
    expected_salary = forms.DecimalField(label='Ожидаемая ЗП, ₽', required=False,
                                          min_value=0, max_digits=10, decimal_places=2,
                                          widget=forms.NumberInput(attrs={'class': 'form-control'}))
    resume = forms.FileField(label='Резюме (PDF / DOCX, до 10 МБ)',
                              widget=forms.FileInput(attrs={'class': 'form-control',
                                                             'accept': '.pdf,.docx,.txt'}))
    cover_letter = forms.CharField(label='Сопроводительное письмо', required=False,
                                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    consent = forms.BooleanField(label='Согласен(на) на обработку персональных данных в '
                                        'соответствии с № 152-ФЗ',
                                  widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def clean_resume(self):
        f = self.cleaned_data['resume']
        if f.size > 10 * 1024 * 1024:
            raise forms.ValidationError('Размер файла не должен превышать 10 МБ.')
        ext = f.name.rsplit('.', 1)[-1].lower()
        if ext not in ('pdf', 'docx', 'txt'):
            raise forms.ValidationError('Поддерживаемые форматы: PDF, DOCX, TXT.')
        return f

    def save(self):
        """Возвращает (candidate, resume). Дедупликация по email/phone."""
        data = self.cleaned_data
        # Дедупликация
        candidate = None
        if data.get('email'):
            candidate = Candidate.objects.filter(email__iexact=data['email']).first()
        if not candidate and data.get('phone'):
            candidate = Candidate.objects.filter(phone=data['phone']).first()
        if not candidate:
            candidate = Candidate.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone', ''),
                expected_salary=data.get('expected_salary'),
            )
        resume = Resume.objects.create(
            candidate=candidate,
            file=data['resume'],
            original_filename=data['resume'].name,
            file_size=data['resume'].size,
            is_primary=True,
        )
        return candidate, resume
