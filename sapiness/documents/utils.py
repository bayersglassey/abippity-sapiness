
import os, glob

from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Document

User = get_user_model()


def create_doc_from_filepath(filepath, unique=False, **kwargs):
    with open(filepath) as f: content = f.read()
    title = os.path.basename(filepath)
    if unique:
        docs = Document.objects.filter(title=title)
        if 'user' in kwargs:
            user = kwargs['user']
            docs = docs.filter(user=user)
        docs.delete()
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


    if 'user' not in kwargs:
        # hardcoded username, good times
        user, created = User.objects.get_or_create(username='tutor')
        #user = User.objects.filter(username='tutor').first()
        kwargs['user'] = user

    if 'unique' not in kwargs: kwargs['unique'] = True
    if 'public_readable' not in kwargs: kwargs['public_readable'] = True

    fileglob = os.path.join(settings.BASE_DIR, os.path.pardir,
        'abippity', 'examples', '*.ab')
    return create_docs_from_glob(fileglob, **kwargs)
