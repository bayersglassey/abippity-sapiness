
import os, glob

from django.conf import settings

from .models import Document


def create_doc_from_filepath(filepath, unique=True, **kwargs):
    with open(filepath) as f: content = f.read()
    title = os.path.basename(filepath)
    if unique: Document.objects.filter(title=title).delete()
    doc = Document.objects.create(title=title, content=content,
        **kwargs)
    return doc

def create_docs_from_glob(fileglob, **kwargs):
    filepaths = glob.glob(fileglob)
    docs = []
    for filepath in filepaths:
        doc = create_doc_from_filepath(filepath, **kwargs)
        docs.append(doc)
    return docs

def update_example_docs(**kwargs):
    """Only works from within the git repo currently containing abippity
    and sapiness - the example files live with abippity."""
    fileglob = os.path.join(settings.BASE_DIR, os.path.pardir,
        'abippity', 'examples', '*.ab')
    return create_docs_from_glob(fileglob, **kwargs)
