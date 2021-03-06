
import io

from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

from abippity.main import main, parse_options, list_args
from abippity.parse import get_keywords_text

from .models import Document

User = get_user_model()


class ArgsHelpView(TemplateView):
    template_name = 'documents/args_help.html'
    def get_context_data(self):
        context = super().get_context_data()
        context['args'] = list_args
        return context

class KeywordsHelpView(TemplateView):
    template_name = 'documents/keywords_help.html'
    def get_context_data(self):
        context = super().get_context_data()
        context['keywords_dump'] = get_keywords_text()
        return context


class DocumentListView(ListView):
    model = Document
    template_name = 'documents/list.html'
    def get_context_data(self):
        context = super().get_context_data()
        username = self.request.GET.get('owner__username')
        if username is not None:
            owner = User.objects.filter(username=username).first()
            context['owner'] = owner
        return context
    def get_queryset(self):
        owner_username = self.request.GET.get('owner__username')
        user = self.request.user
        if not user.is_authenticated: user = None
        queryset = super().get_queryset()
        if owner_username is not None:
            queryset = queryset.filter(user__username=owner_username)
        queryset = Document.filter_readable(queryset, user=user)
        return queryset

class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/detail.html'

    def get_context_data(self, object):
        context = super().get_context_data(object=object)
        context['args'] = '--run --report'
        context['writable'] = object.writable_for_user(self.request.user)
        return context

    def dispatch(self, request, *args, **kwargs):
        # From DetailView.get:
        doc = self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # Make sure user is allowed to see the document:
        if not doc.readable_for_user(request.user):
            msg = ("You don't have permission to see this "
                "document: {}".format(doc.title))
            return HttpResponse(msg, status=403)

        # User clicks "RUN":
        if 'run' in request.POST:
            # Get args from POST, parse as abippity options
            args_text = request.POST.get('args', '')
            args = args_text.split()
            options = parse_options(args)

            # Run abippity interpreter on document's content
            output = self.run(doc.content, options)

            context['args'] = args_text
            context['output'] = output

        # From DetailView.get:
        return self.render_to_response(context)

    def run(self, text, options):
        """Wrapper around abippity.main, returning its output as a str"""

        # Hack, abippity.main just uses print statements with file=file,
        # we pass it a StringIO as file in order to get text we can
        # stuff into the response...
        output_io = io.StringIO()

        # Run abippity interpreter
        try:
            main(text, options, file=output_io)
        except (ValueError, TypeError, AssertionError) as e:
            # TODO: Make AbippityException or whatever, so we don't
            # accidentally show users errors they were never meant to
            # see...
            msg = "*** ERROR: {}".format(e)
            output_io.write(msg)

        # Read the output of abippity.main, stick it in the context to
        # be rendered
        output_io.seek(0)
        output = output_io.read()

        return output


class DocumentDeleteView(DetailView):
    model = Document
    template_name = 'documents/delete.html'
    def dispatch(self, request, *args, **kwargs):
        # From DetailView.get:
        doc = self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # Make sure user is allowed to delete the document:
        if not doc.writable_for_user(request.user):
            msg = ("You don't have permission to delete this "
                "document: {}".format(doc.title))
            return HttpResponse(msg, status=403)

        # User clicks "Yes, I want to delete it":
        if 'delete' in request.POST:
            doc.delete()
            return redirect('home')

        # From DetailView.get:
        return self.render_to_response(context)


class DocumentEditViewMixin:
    model = Document
    fields = ['title', 'content', 'public_readable', 'public_writable']
    template_name = 'documents/edit.html'
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if not user or not user.is_authenticated:
            public_readable = form.fields['public_readable']
            public_writable = form.fields['public_writable']
            for field in [public_readable, public_writable]:
                field.initial = True
                field.disabled = True
        return form
    def get_success_url(self):
        return reverse('documents:detail', kwargs={'pk': self.object.pk})

class DocumentEditView(DocumentEditViewMixin, UpdateView): pass
class DocumentCreateView(DocumentEditViewMixin, CreateView):
    def get_initial(self):
        initial = super().get_initial()

        copy_id = self.request.GET.get('copy_id')
        copy_doc = Document.objects.filter(id=copy_id).first()
        if copy_doc is not None:
            initial['title'] = "{} (Copy)".format(copy_doc.title)
            initial['content'] = copy_doc.content

        return initial
    def form_valid(self, form):
        doc = form.save(commit=False)
        user = self.request.user
        if user and user.is_authenticated:
            doc.user = user
        doc.save()
        self.object = doc
        return super().form_valid(form)

