from django import forms
from .models import HiringRequest, Vacancy


class HiringRequestForm(forms.ModelForm):
    class Meta:
        model = HiringRequest
        fields = ('title', 'description', 'department', 'position',
                  'salary_min', 'salary_max', 'urgency')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ('title', 'description', 'requirements', 'benefits',
                  'recruiter', 'hiring_manager', 'min_experience_years', 'deadline')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'benefits': forms.Textarea(attrs={'rows': 3}),
        }
