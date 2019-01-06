from django.db import models

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

    def readable_for_user(self, user):
        return (self.public_readable or self.user == user or
            user and user.is_superuser)

    def writable_for_user(self, user):

        # Anonymous users can't modify documents.
        # Somewhat arbitrary. *shrug*
        if user is None or not user.is_authenticated: return False

        return (self.public_writable or self.user == user or
            user and user.is_superuser)
