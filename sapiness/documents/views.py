
import io

from django.http import HttpResponse
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

from abipitty.main import main, parse_options, list_args
from abipitty.lib.parse import get_keywords_text

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
        user = self.request.user
        if not user.is_authenticated: user = None
        queryset = super().get_queryset()
        owner_username = self.request.GET.get('owner__username')
        if owner_username is not None:
            queryset = queryset.filter(user__username=owner_username)
        if not user or not user.is_superuser:
            queryset = queryset.filter(
                Q(public_readable=True) | Q(user=user))
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
            # Get args from POST, parse as abipitty options
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

        # Hack, abipitty.main just uses print statements with file=file,
        # we pass it a StringIO as file in order to get text we can
        # stuff into the response...
        output_io = io.StringIO()

        # Run abipitty interpreter
        try:
            main(text, options, file=output_io)
        except (ValueError, TypeError, AssertionError) as e:
            # TODO: Make AbippityException or whatever, so we don't
            # accidentally show users errors they were never meant to
            # see...
            msg = "*** ERROR: {}".format(e)
            output_io.write(msg)

        # Read the output of abipitty.main, stick it in the context to
        # be rendered
        output_io.seek(0)
        output = output_io.read()

        return output
