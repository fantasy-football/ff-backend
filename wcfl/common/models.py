from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    profile_picture = models.URLField()
    email = models.EmailField()
    squad_created = models.BooleanField(default=False)
    score = models.SmallIntegerField(default=0)
    balance = models.SmallIntegerField(default=100)
    round = models.SmallIntegerField(default=0)

    def __str__(self):
        return "<ID {} {}>".format(self.id, self.name)

    class Meta:
        ordering = ["-score"]
        verbose_name_plural = "Users"
