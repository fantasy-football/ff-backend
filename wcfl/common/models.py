from django.db import models


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100, null=False, blank=False)
    profile_picture = models.URLField(null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    squad_created = models.BooleanField(default=False)
    score = models.SmallIntegerField(default=0)
    balance = models.SmallIntegerField(default=100)
    current_round = models.SmallIntegerField(default=0)

    def __str__(self):
        return "<ID {} {}>".format(self.id, self.name)

    class Meta:
        ordering = ["-score"]
        verbose_name_plural = "Users"
