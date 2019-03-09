'''
  Parameters:

  1ª: Home team name
  2ª: Away team name
  3ª: Date that a match has occurred
'''
BASE_URL = 'https://futebol.placar.esporte.uol.com.br/api/v2/geral/placares.htm?modalidade=futebol&filename={}-x-{}&data={}000000&idCompeticao=30'
CSV_FILE = 'data/BRA.csv'
DATABASE_NAME = 'br-league.db'