
import io

from django.views.generic import ListView, DetailView
from django.views.generic import TemplateView

from abipitty.main import main, parse_options, list_args
from abipitty.lib.parse import get_keywords_text

from .models import Document


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

class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/detail.html'

    def get_context_data(self, object):
        context = super().get_context_data(object=object)
        context['args'] = '--run --report'
        return context

    def dispatch(self, request, *args, **kwargs):
        # From DetailView.get:
        doc = self.object = self.get_object()
        context = self.get_context_data(object=self.object)

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
        main(text, options, file=output_io)

        # Read the output of abipitty.main, stick it in the context to
        # be rendered
        output_io.seek(0)
        output = output_io.read()

        return output
