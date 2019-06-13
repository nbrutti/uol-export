from config.defs import *
import peewee

db = peewee.SqliteDatabase(DATABASE_NAME)

class BaseModel(peewee.Model):
  class Meta:
    database = db

class Partida(BaseModel):
  id_time_casa = peewee.CharField()
  id_time_visitante = peewee.CharField()
  time_casa = peewee.CharField()
  time_visitante = peewee.CharField()
  data = peewee.DateField()
  time_da_casa_venceu = peewee.IntegerField()
  HG = peewee.FloatField()
  AG = peewee.FloatField()
  PH = peewee.FloatField()
  PD = peewee.FloatField()
  PA = peewee.FloatField()
  MAX_H = peewee.FloatField()
  MAX_D = peewee.FloatField()
  MAX_A = peewee.FloatField()
  AVG_H = peewee.FloatField()
  AVG_D = peewee.FloatField()
  AVG_A = peewee.FloatField()

  class Meta:
    db_table = 'partidas'

class Substituicao(BaseModel):
  # Pode ser INTERVALO
  tempo = peewee.CharField()
  tipo_tatico = peewee.CharField(null=True)
  efetividade = peewee.IntegerField()

  class Meta:
    db_table = 'substituicoes'

class Penalti(BaseModel):
  tempo = peewee.CharField()

  class Meta:
    db_table = 'penaltis'

class CartaoAmarelo(BaseModel):
  tempo = peewee.CharField()
  id_jogador = peewee.CharField()

  class Meta:
    db_table = 'cartoes_amarelos'

class CartaoVermelho(BaseModel):
  tempo = peewee.CharField()
  id_jogador = peewee.CharField()

  class Meta:
    db_table = 'cartoes_vermelhos'

class GolContra(BaseModel):
  tempo = peewee.CharField()
  id_jogador = peewee.CharField()

  class Meta:
    db_table = 'gols_contra'

class Gol(BaseModel):
  tempo = peewee.CharField()
  id_jogador = peewee.CharField()

  class Meta:
    db_table = 'gols'

class Time(BaseModel):
  api_id = peewee.IntegerField()
  nome   = peewee.CharField()
  class Meta:
    db_table = "times"

### Relacionamentos ###

class PartidasSubstituicoes(BaseModel):
  partida = peewee.ForeignKeyField(Partida)
  substituicao = peewee.ForeignKeyField(Substituicao)
  
  class Meta:
    db_table = 'partidas_substituicoes'

class PartidasPenaltis(BaseModel):
  partida = peewee.ForeignKeyField(Partida)
  penalti = peewee.ForeignKeyField(Penalti)

  class Meta:
    db_table = 'partidas_penaltis'

class PartidasCartoesAmarelos(BaseModel):
  partida = peewee.ForeignKeyField(Partida)
  cartoes_amarelos = peewee.ForeignKeyField(CartaoAmarelo)

  class Meta:
    db_table = 'partidas_cartoes_amarelos'

class PartidasCartoesVermelhos(BaseModel):
  partida = peewee.ForeignKeyField(Partida)
  cartoes_vermelhos = peewee.ForeignKeyField(CartaoVermelho)

  class Meta:
    db_table = 'partidas_cartoes_vermelhos'

class PartidasGolsContra(BaseModel):
  partida = peewee.ForeignKeyField(Partida)
  gols_contra = peewee.ForeignKeyField(GolContra)

  class Meta:
    db_table = 'partidas_gols_contra'

class PartidasGols(BaseModel):
  partida = peewee.ForeignKeyField(Partida)
  gols = peewee.ForeignKeyField(Gol)

  class Meta:
    db_table = 'partidas_gols'

db.create_tables([Partida, Substituicao, Penalti, CartaoAmarelo, CartaoVermelho, GolContra, Gol, Time])
db.create_tables([PartidasSubstituicoes, PartidasPenaltis, PartidasCartoesAmarelos, PartidasCartoesVermelhos, PartidasGolsContra, PartidasGols])