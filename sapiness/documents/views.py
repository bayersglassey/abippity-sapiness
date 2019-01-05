
from django.views.generic import ListView, DetailView

from .models import Document


class DocumentListView(ListView):
    model = Document
    template_name = 'documents/list.html'

class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/detail.html'
