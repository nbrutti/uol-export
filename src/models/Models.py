from config.defs import *
import peewee

db = peewee.SqliteDatabase(DATABASE_NAME)

class BaseModel(peewee.Model):
  class Meta:
    database = db

class Match(BaseModel):
  team_home_id = peewee.CharField()
  team_away_id = peewee.CharField()
  team_home = peewee.CharField()
  team_away = peewee.CharField()
  date = peewee.DateField()

  class Meta:
    db_table = 'matches'

class Substitution(BaseModel):
  # Pode ser INTERVALO
  time = peewee.CharField()

  class Meta:
    db_table = 'substitutions'

class Penalty(BaseModel):
  time = peewee.CharField()

  class Meta:
    db_table = 'penaltys'

class YellowCard(BaseModel):
  time = peewee.CharField()
  player_id = peewee.CharField()

  class Meta:
    db_table = 'ycards'

class RedCard(BaseModel):
  time = peewee.CharField()
  player_id = peewee.CharField()

  class Meta:
    db_table = 'rcards'

class GoalsAgainst(BaseModel):
  time = peewee.CharField()
  player_id = peewee.CharField()

  class Meta:
    db_table = 'against_goals'

class Goal(BaseModel):
  time = peewee.CharField()
  player_id = peewee.CharField()

  class Meta:
    db_table = 'goals'

### Relationships ###

class MatchSubstitution(BaseModel):
  match = peewee.ForeignKeyField(Match)
  substitution = peewee.ForeignKeyField(Substitution)
  
  class Meta:
    db_table = 'match_substitution'

class MatchPenalty(BaseModel):
  match = peewee.ForeignKeyField(Match)
  penalty = peewee.ForeignKeyField(Penalty)

  class Meta:
    db_table = 'match_penalty'

class MatchYcard(BaseModel):
  match = peewee.ForeignKeyField(Match)
  y_card = peewee.ForeignKeyField(YellowCard)

  class Meta:
    db_table = 'match_ycards'

class MatchRcard(BaseModel):
  match = peewee.ForeignKeyField(Match)
  r_card = peewee.ForeignKeyField(RedCard)

  class Meta:
    db_table = 'match_rcards'

class MatchAgainstGoal(BaseModel):
  match = peewee.ForeignKeyField(Match)
  against_goal = peewee.ForeignKeyField(GoalsAgainst)

  class Meta:
    db_table = 'match_against_goals'

class MatchGoal(BaseModel):
  match = peewee.ForeignKeyField(Match)
  goal = peewee.ForeignKeyField(Goal)

  class Meta:
    db_table = 'match_goals'

db.create_tables([Match, Substitution, Penalty, YellowCard, RedCard, GoalsAgainst, Goal])
db.create_tables([MatchSubstitution, MatchPenalty, MatchYcard, MatchRcard, MatchAgainstGoal, MatchGoal])