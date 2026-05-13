from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import FeedbackForm


def feedback_form(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Спасибо! Мы получили ваше сообщение и ответим '
                                       'в течение 2 рабочих дней.')
            return redirect('feedback')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/form.html', {
        'form': form,
        'breadcrumbs': [('Главная', '/'), ('Обратная связь', None)],
    })
