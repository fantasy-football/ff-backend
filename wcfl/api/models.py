from django.db import models

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

import requests


class Team(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=18)
    trigram = models.CharField(max_length=3, default="NAN")
    prequarter_finalist = models.BooleanField(default=False)
    quarter_finalist = models.BooleanField(default=False)
    semi_finalist = models.BooleanField(default=False)
    finalist = models.BooleanField(default=False)
    flag = models.ImageField(upload_to='teams/', blank=True, null=True)
    flag_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '<{0}: {1}>'.format(self.id, self.name)

    class Meta:
        verbose_name_plural = 'Teams'
        ordering = ['id']

    def cache_image(self):
        try:
            response = requests.get(self.flag_url)
            if response.status_code == requests.codes.ok:
                filename = self.trigram + '.png'

                try:
                    temp_file = NamedTemporaryFile()
                    temp_file.write(response.content)
                    temp_file.flush()

                except Exception as e:
                    print("Error writing image to file", e)

                self.flag.save(filename, File(temp_file), save=True)
                print("Successfully created", filename)

        except Exception as e:
            print("Error fetching image", e)


class Player(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    GOALKEEPER = 'GK'
    DEFENDER = 'DEF'
    MIDFIELDER = 'MID'
    FORWARD = 'FW'

    POSITION_CHOICES = (
            (GOALKEEPER, 'Goalkeeper'),
            (DEFENDER, 'Defender'),
            (MIDFIELDER, 'Midfielder'),
            (FORWARD, 'Forward'),
        )

    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    points = models.SmallIntegerField(default=0)
    value = models.FloatField(null=False)

    def __str__(self):
        return '<{0}: {1} ({2})>'.format(self.id, self.name, self.team.name)

    class Meta:
        ordering = ['-points', 'id', 'team', 'position']
        verbose_name_plural = 'Players'


class SquadLimit(models.Model):
    round = models.SmallIntegerField(default=0)
    limit = models.SmallIntegerField(default=3)

    def __str__(self):
        return '<Round {}>'.format(self.round)

    class Meta:
        verbose_name_plural = 'SquadLimits'
        ordering = ['round']


class Squad(models.Model):
    user = models.OneToOneField('common.User', on_delete=models.CASCADE,
                                primary_key=True)
    players = models.ManyToManyField('Player')
    captain = models.ForeignKey('Player', on_delete=models.CASCADE,
                                related_name='captain')
    vice_captain = models.ForeignKey('Player', on_delete=models.CASCADE,
                                     related_name='vice_captain')

    def __str__(self):
        return '<{0}: {1}>'.format(self.user.id, self.user.name)

    class Meta:
        verbose_name_plural = 'Squads'


class Fixture(models.Model):
    id = models.AutoField(primary_key=True)
    team1 = models.ForeignKey('Team', on_delete=models.CASCADE,
                              related_name='team1')
    team2 = models.ForeignKey('Team', on_delete=models.CASCADE,
                              related_name='team2')
    score1 = models.SmallIntegerField(default=0)
    score2 = models.SmallIntegerField(default=0)
    gametime = models.DateTimeField('Game Played')
    completed = models.BooleanField(default=False)

    def __str__(self):
        return '<{0}: {1} {2}-{4} {3}>'.format(self.gametime,
                                                self.team1.name, self.score1,
                                                self.team2.name, self.score2)

    class Meta:
        verbose_name_plural = 'Fixtures'
        ordering = ['id']


class LineUp(models.Model):
    fixture = models.OneToOneField('Fixture', primary_key=True,
                                   on_delete=models.CASCADE)
    players = models.ManyToManyField('Player')

    def __str__(self):
        return '<{0}: {1} vs {2}>'.format(self.fixture.id,
                                          self.fixture.name)

    class Meta:
        verbose_name_plural = 'LineUps'
