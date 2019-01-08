from django.db import models
from django.db.models import Q

from django.contrib.auth import get_user_model

User = get_user_model()


class Document(models.Model):

    title = models.CharField("Title", max_length=200)
    content = models.TextField("Content")
    user = models.ForeignKey(User, verbose_name="User",
        null=True, blank=True)
    public_readable = models.BooleanField("Public (Readable)", default=False)
    public_writable = models.BooleanField("Public (Writable)", default=False)

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<Document {}: {}>".format(self.id, self)

    def readable_for_user(self, user=None):
        if user and user.is_superuser: return True
        return self.public_readable or self.user and self.user == user

    def writable_for_user(self, user=None):
        if user and user.is_superuser: return True
        return self.public_writable or self.user and self.user == user

    @staticmethod
    def filter_readable(queryset, user=None):
        # model managers? feh
        if user and user.is_superuser: return queryset
        q = Q(public_readable=True)
        if user: q |= Q(user=user)
        return queryset.filter(q)

    @staticmethod
    def filter_writable(queryset, user=None):
        # model managers? feh
        if user and user.is_superuser: return queryset
        q = Q(public_writable=True)
        if user: q |= Q(user=user)
        return queryset.filter(q)

