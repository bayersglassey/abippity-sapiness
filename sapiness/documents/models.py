from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Document(models.Model):

    title = models.CharField("Title", max_length=200)
    content = models.TextField("Content")
    user = models.ForeignKey(User, verbose_name="User",
        null=True, blank=True)
    public_read = models.BooleanField("Public (Readable)", default=False)
    public_write = models.BooleanField("Public (Writable)", default=False)

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<Document {}: {}>".format(self.id, self)

    def readable_for_user(self, user):
        return self.public_read or not self.user or self.user == user

    def writable_for_user(self, user):

        # Anonymous users can't modify documents.
        # Somewhat arbitrary. *shrug*
        if user is None: return False

        return self.public_write or not self.user or self.user == user
