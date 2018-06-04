from django.contrib import admin
from .models import Team, Player, Squad, SquadLimit, Fixture, LineUp

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Squad)
admin.site.register(SquadLimit)
admin.site.register(Fixture)
admin.site.register(LineUp)
