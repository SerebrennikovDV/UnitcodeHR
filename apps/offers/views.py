from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Offer
from .services import generate_offer_docx


@login_required
def offer_list(request):
    offers = Offer.objects.select_related('application__candidate', 'application__vacancy')\
                          .order_by('-created_at')
    return render(request, 'offers/offer_list.html', {
        'offers': offers,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Офферы', None)],
    })


@login_required
def offer_detail(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    return render(request, 'offers/offer_detail.html', {
        'offer': offer,
        'breadcrumbs': [('Дашборд', '/dashboard/'), ('Офферы', '/offers/'),
                         (f'Оффер #{offer.pk}', None)],
    })


@login_required
def offer_generate_docx(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    generate_offer_docx(offer)
    messages.success(request, '.docx-файл оффера сгенерирован.')
    return redirect('offer_detail', pk=offer.pk)


@login_required
def offer_download(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    if not offer.document:
        generate_offer_docx(offer)
    return FileResponse(offer.document.open('rb'),
                        as_attachment=True,
                        filename=offer.document.name.split('/')[-1])
