from django.db import models

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

import requests

from common.models import User


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
    FORWARD = 'FWD'

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

    
    @classmethod
    def reset_points(cls, player_id):
        player = cls.objects.get(id=player_id)
        player.points = 0
        player.save()


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
    
    starting = models.ManyToManyField('Player')
    
    captain = models.ForeignKey('Player', on_delete=models.CASCADE,
                                related_name='captain')
    
    vice_captain = models.ForeignKey('Player', on_delete=models.CASCADE,
                                     related_name='vice_captain')
    
    substitutes = models.ManyToManyField('Player', related_name='substitute')

    def __str__(self):
        return '<{0}: {1}>'.format(self.user.id, self.user.name)

    class Meta:
        verbose_name_plural = 'Squads'

    @classmethod
    def create(cls, user_id, starting_list, substitutes, captain_id, vice_captain_id):
        try:
            user = User.objects.get(id = user_id)
        
            try:
                captain = Player.objects.get(id = captain_id)
                vice_captain = Player.objects.get(id = vice_captain_id)

            except Exception as e:
                print(" Invalid captain/vc")

            x = cls(user = user,
                captain = captain,
                vice_captain = vice_captain)

            x.save()
            
            try:
                for player_id in starting_list:
                    player = Player.objects.get(id = player_id)
                    x.starting.add(player)

                for player_id in substitutes:
                    substitute = Player.objects.get(id = player_id)
                    x.substitutes.add(substitute)

                x.save()

            except Exception as e:
                print("Could not add squad")
                x.delete()
            
            user.squad_created = True
            user.save()

            return x

        except Exception as e:
            print("User not authorized, invalid request")
        
    
    def compute_score(self):
        net_points = 0
        
        vcInSub = False
        capSub = False
        
        for player in self.substitutes.all():
            if player.name == self.captain.name:
                capSub = True
            if player.name == self.vice_captain.name:
                vcInSub = True
         
        if capSub == False:
            net_points += 3 * (self.captain.points)  
	
        if vcInSub == False:
            net_points += 2 * (self.vice_captain.points)

        for player in self.starting.all():
            net_points += player.points
        
        for player in self.substitutes.all():
            if player.name == self.captain.name:
                net_points += (3*player.points)//2
            
            elif player.name == self.vice_captain.name:
                net_points += player.points

            else:
                net_points += player.points//2

        return net_points

    
    def get_data(self):
        
        data = []
        
        vcInSub = False
        capSub = False
        
        for player in self.substitutes.all():
            if player.name == self.captain.name:
                capSub = True
            if player.name == self.vice_captain.name:
                vcInSub = True
                
        if capSub == False:
            data.append({'name': self.captain.name, 'position': self.captain.position,
                         'points': 3*self.captain.points, 'isCaptain': True,
                         'trigram': self.captain.team.trigram,
			 'isSub': False
                        })
        
        if vcInSub == False:
            data.append({'name': self.vice_captain.name, 'position': self.vice_captain.position,
                         'points': 2*self.vice_captain.points, 'isVC': True,
                         'trigram': self.vice_captain.team.trigram,
			 'isSub': False
                        })


        for index, player in enumerate(self.starting.all()):
            data.append({'name': player.name, 
                         'position': player.position,
                         'points': player.points,
                         'trigram': player.team.trigram,
			 'isSub': False
                         })
       
        

        for index, player in enumerate(self.substitutes.all()):
            if player.name == self.captain.name:
                data.append({'name': player.name, 
                             'position': player.position,
                             'points': (3*player.points)//2,
                             'trigram': player.team.trigram,
                             'isSub': True
                            })

            elif player.name == self.vice_captain.name: 
                data.append({'name': player.name, 
                             'position': player.position,
                             'points': (player.points)//2,
                             'trigram': player.team.trigram,
                             'isSub': True
                            })
            
            else:
                data.append({'name': player.name, 
                             'position': player.position,
                             'points': (player.points)//2,
                             'trigram': player.team.trigram,
                             'isSub': True
                            })        
        
        return data



    def transfer_data(self):
        
        data = []
        
        vcInSub = False
        capSub = False
        
        for player in self.substitutes.all():
            if player.name == self.captain.name:
                capSub = True
            if player.name == self.vice_captain.name:
                vcInSub = True
                
        if capSub == False:
            data.append({'name': self.captain.name, 'position': self.captain.position,
                         'points': 3*self.captain.points, 'isCaptain': True,
                         'trigram': self.captain.team.trigram, 'value': self.captain.value,
			 'isSub': False, 'id': self.captain.id
                        })
        
        if vcInSub == False:
            data.append({'name': self.vice_captain.name, 'position': self.vice_captain.position,
                         'points': 2*self.vice_captain.points, 'isVC': True,
                         'trigram': self.vice_captain.team.trigram,
			 'isSub': False, 'id': self.vice_captain.id
                        })


        for index, player in enumerate(self.starting.all()):
            data.append({'name': player.name, 
                         'position': player.position,
                         'points': player.points,
                         'trigram': player.team.trigram,
			 'isSub': False,
			 'id': self.player.id,
			 'value': self.player.value, 
                         })
       
        

        for index, player in enumerate(self.substitutes.all()):
            if player.name == self.captain.name:
                data.append({'name': player.name, 
                             'position': player.position,
                             'points': (3*player.points)//2,
                             'trigram': player.team.trigram,
			     'value': self.player.value,
			     'id': self.player.id,
                             'isSub': True
                            })

            elif player.name == self.vice_captain.name: 
                data.append({'name': player.name, 
                             'position': player.position,
                             'points': (player.points)//2,
                             'trigram': player.team.trigram,
			     'value': self.player.value,
			     'id': self.player.id,
                             'isSub': True
                            })
            
            else:
                data.append({'name': player.name, 
                             'position': player.position,
                             'points': (player.points)//2,
                             'trigram': player.team.trigram,
                             'isSub': True
                            })        
        
        return data


    @classmethod
    def compute_value(cls, user):
            
        squad_value = 0

        squad = cls.objects.get(user=user)

        vcInSub = False
        capSub = False
        
        for player in squad.substitutes.all():
            if player.name == squad.captain.name:
                capSub = True
            if player.name == squad.vice_captain.name:
                vcInSub = True
    
        if not capSub:
           squad_value += squad.captain.value

        if not vcInSub:
           squad_value += squad.vice_captain.value

        for player in squad.starting.all():
            squad_value += player.value

        for player in squad.substitutes.all():
            squad_value += player.value
      
        return squad_value

           
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


class Transfer(models.Model):
    user = models.OneToOneField('common.User', on_delete=models.CASCADE,
                                primary_key=True)
    
    starting = models.ManyToManyField('Player')
    
    captain = models.ForeignKey('Player', on_delete=models.CASCADE,
                                related_name='transferCap')
    
    vice_captain = models.ForeignKey('Player', on_delete=models.CASCADE,
                                     related_name='transferVC')
    
    substitutes = models.ManyToManyField('Player', related_name='transferSubs')

    
    def __str__(self):
        return '<{0}: {1}>'.format(self.user.id, self.user.name)

    
    class Meta:
        verbose_name_plural = 'Transfers'

    
    @classmethod
    def create(cls, user_id, starting_list, substitutes, captain_id, vice_captain_id):
        try:
            user = User.objects.get(id = user_id)
        
            try:
                captain = Player.objects.get(id = captain_id)
                vice_captain = Player.objects.get(id = vice_captain_id)

            except Exception as e:
                print(" Invalid captain/vc")

            x = cls(user = user,
                captain = captain,
                vice_captain = vice_captain)

            x.save()
            
            try:
                for player_id in starting_list:
                    player = Player.objects.get(id = player_id)
                    x.starting.add(player)

                for player_id in substitutes:
                    substitute = Player.objects.get(id = player_id)
                    x.substitutes.add(substitute)

                x.save()

            except Exception as e:
                print("Could not add squad")
                x.delete()
            
            user.squad_created = True
            user.save()

            return x

        except Exception as e:
            print("User not authorized, invalid request")
        

class PlayerStat(models.Model):
    player = models.OneToOneField('Player', on_delete=models.CASCADE,
			       primary_key=True)
    goals = models.SmallIntegerField(default=0)
    assists = models.SmallIntegerField(default=0)
    yellow_cards = models.SmallIntegerField(default=0)
    red_cards = models.SmallIntegerField(default=0)
    total_points = models.SmallIntegerField(default=0)

    def __str__(self):
        return '<{0}: {1} {2}>'.format(self.player.id, self.player.name, self.total_points)

    class Meta:
        verbose_name_plural = 'PlayerStats'
        ordering = ['-total_points', 'goals']
    

    @classmethod
    def create(cls, player, player_points):
        x = cls(player=player,
                total_points = player_points)
        x.save()
       
    @classmethod
    def update(cls, player, player_points):
        x = cls.objects.get(player=player)
        x.total_points += player_points
        x.save()   
