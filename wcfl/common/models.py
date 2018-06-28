from django.db import models


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100, null=False, blank=False)
    profile_picture = models.URLField(null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    squad_created = models.BooleanField(default=False)
    score = models.SmallIntegerField(default=0)
    balance = models.FloatField(default=100)
    current_round = models.SmallIntegerField(default=0)

    def __str__(self):
        return "<ID {} {}>".format(self.id, self.name)

    class Meta:
        ordering = ['-score']
        verbose_name_plural = 'Users'

    @classmethod
    def reset_squad(cls, user_id):
        x = cls.objects.get(id=user_id)
        x.squad_created = False
        x.current_round += 1
        x.save()


class UserStat(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE,
	                        primary_key=True)
    total_score = models.SmallIntegerField(default = 0)

    def __str__(self):
        return '<{0}: {1}, {2}>'.format(self.user.id, self.user.name, self.total_score)

    class Meta:
        ordering = ['-total_score']
        verbose_name_plural = 'UserStats'

     
    @classmethod
    def create(cls, user, round_score):
        x = cls(user=user,
                total_score=round_score 
                )
        x.save()

    @classmethod
    def update(cls, user, round_score):
        x = cls.objects.get(user=user)
        x.total_score += round_score
        x.save()

