from django.db import models


class Document(models.Model):
    title = models.CharField("Title", max_length=200)
    content = models.TextField("Content")
