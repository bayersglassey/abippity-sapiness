
import io

from django.views.generic import ListView, DetailView

from abipitty.main import main

from .models import Document


class DocumentListView(ListView):
    model = Document
    template_name = 'documents/list.html'

class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/detail.html'
    def post(self, request, *args, **kwargs):
        # From DetailView.get:
        doc = self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if 'run' in request.POST:
            # Hack, abipitty.main just uses print statements with file=file,
            # we psas it a StringIO as file in order to get text we can
            # stuff into the response...
            output_io = io.StringIO()

            # Run abipitty on the document's content:
            options = dict(RUN=True, PRINT_REPORT=True)
            main(doc.content, options, file=output_io)

            # Read the output of abipitty.main, stick it in the context to
            # be rendered
            output_io.seek(0)
            output = output_io.read()
            context['output'] = output

        # From DetailView.get:
        return self.render_to_response(context)
