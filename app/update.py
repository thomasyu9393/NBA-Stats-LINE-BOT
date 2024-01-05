import requests
from bs4 import BeautifulSoup
import configparser
import psycopg2
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

config = configparser.ConfigParser()
config.read('config.ini')

DB_HOST = config.get('database', 'DB_HOST')
DB_PORT = config.getint('database', 'DB_PORT')
DB_USER = config.get('database', 'DB_USER')
DB_PASSWORD = config.get('database', 'DB_PASSWORD')
DB_NAME = config.get('database', 'DB_NAME')

def scrape_and_update():
	try:
		url = 'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'
		response = requests.get(url)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			players = soup.find('table', {'id': 'per_game_stats'}).find('tbody').find_all('tr', {'class': 'full_table'})
			name_count = {}
			for player in players:
				name = player.find('td', {'data-stat': 'player'}).text
				name_count[name] = name_count.get(name, 0) + 1
			multiple = [name for name, count in name_count.items() if count > 1]
			updated_players = [player for player in players if (player.find('td', {'data-stat': 'player'}).text not in multiple) or (player.find('td', {'data-stat': 'pos'}).text == 'TOT')]
			try:
				connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
				cursor = connection.cursor()
				for player in updated_players:
					name     = player.find('td', {'data-stat': 'player'}).text
					name = name.replace("'", "''")
					position = player.find('td', {'data-stat': 'pos'}).text
					age      = player.find('td', {'data-stat': 'age'}).text
					team_id  = player.find('td', {'data-stat': 'team_id'}).text
					GP       = player.find('td', {'data-stat': 'g'}).text
					MinP     = player.find('td', {'data-stat': 'mp_per_g'}).text
					FG       = player.find('td', {'data-stat': 'fg_per_g'}).text
					FGA      = player.find('td', {'data-stat': 'fga_per_g'}).text
					threeP   = player.find('td', {'data-stat': 'fg3_per_g'}).text
					threePA  = player.find('td', {'data-stat': 'fg3a_per_g'}).text
					FT  = player.find('td', {'data-stat': 'ft_per_g'}).text
					FTA = player.find('td', {'data-stat': 'fta_per_g'}).text
					ORB = player.find('td', {'data-stat': 'orb_per_g'}).text
					DRB = player.find('td', {'data-stat': 'drb_per_g'}).text
					AST = player.find('td', {'data-stat': 'ast_per_g'}).text
					STL = player.find('td', {'data-stat': 'stl_per_g'}).text
					BLK = player.find('td', {'data-stat': 'blk_per_g'}).text
					TOV = player.find('td', {'data-stat': 'tov_per_g'}).text
					PF  = player.find('td', {'data-stat': 'pf_per_g'}).text
					PTS = player.find('td', {'data-stat': 'pts_per_g'}).text
					# player_shooting
					sql_query = "update player_shooting " \
								f"set player_fgm = {FG}, player_fga = {FGA}, player_3pm = {threeP}, " \
								f"player_3pa = {threePA}, player_ftm = {FT}, player_fta = {FTA} " \
								f"where player_name = '{name}'"
					cursor.execute(sql_query)
					connection.commit()
					# player_stats
					sql_query = "update player_stats " \
								f"set player_oreb = {ORB}, player_dreb = {DRB}, player_ast = {AST}, player_stl = {STL}, " \
								f"player_blk = {BLK}, player_tov = {TOV}, player_pf = {PF}, player_pts = {PTS} " \
								f"where player_name = '{name}'"
					cursor.execute(sql_query)
					connection.commit()
					# player_info
					sql_query = "update player_info " \
								f"set pos = '{position}', age = {age}, team_code = '{team_id}', player_gp = {GP}, player_min = {MinP} " \
								f"where player_name = '{name}'"
					cursor.execute(sql_query)
					connection.commit()
				
				url = 'https://www.basketball-reference.com/leagues/NBA_2024.html'
				response = requests.get(url)
				soup = BeautifulSoup(response.text, 'html.parser')
				teams = soup.find('table', {'id': 'per_game-team'}).find('tbody').find_all('tr')
				for team in teams:
					name    = team.find('td', {'data-stat': 'team'}).text
					GP      = team.find('td', {'data-stat': 'g'}).text
					FG      = team.find('td', {'data-stat': 'fg'}).text
					FGA     = team.find('td', {'data-stat': 'fga'}).text
					threeP  = team.find('td', {'data-stat': 'fg3'}).text
					threePA = team.find('td', {'data-stat': 'fg3a'}).text
					FT  = team.find('td', {'data-stat': 'ft'}).text
					FTA = team.find('td', {'data-stat': 'fta'}).text
					ORB = team.find('td', {'data-stat': 'orb'}).text
					DRB = team.find('td', {'data-stat': 'drb'}).text
					AST = team.find('td', {'data-stat': 'ast'}).text
					STL = team.find('td', {'data-stat': 'stl'}).text
					BLK = team.find('td', {'data-stat': 'blk'}).text
					TOV = team.find('td', {'data-stat': 'tov'}).text
					PF  = team.find('td', {'data-stat': 'pf'}).text
					PTS = team.find('td', {'data-stat': 'pts'}).text
					# team_shooting
					sql_query = "update team_shooting " \
								f"set team_fgm = {FG}, team_fga = {FGA}, team_3pm = {threeP}, " \
								f"team_3pa = {threePA}, team_ftm = {FT}, team_fta = {FTA} " \
								f"where team_name = '{name}'"
					cursor.execute(sql_query)
					connection.commit()
					# team_stats
					sql_query = "update team_stats " \
								f"set team_oreb = {ORB}, team_dreb = {DRB}, team_ast = {AST}, team_stl = {STL}, " \
								f"team_blk = {BLK}, team_tov = {TOV}, team_pf = {PF}, team_pts = {PTS} " \
								f"where team_name = '{name}'"
					cursor.execute(sql_query)
					connection.commit()
					# team_info
					sql_query = "update team_info " \
								f"set team_gp = '{GP}' " \
								f"where team_name = '{name}'"
					cursor.execute(sql_query)
					connection.commit()
				opp_teams = soup.find('table', id='per_game-opponent').find('tbody').find_all('tr')
				for team in opp_teams:
					name    = team.find('td', {'data-stat': 'team'}).text
					FG      = team.find('td', {'data-stat': 'opp_fg'}).text
					FGA     = team.find('td', {'data-stat': 'opp_fga'}).text
					threeP  = team.find('td', {'data-stat': 'opp_fg3'}).text
					threePA = team.find('td', {'data-stat': 'opp_fg3a'}).text
					FT  = team.find('td', {'data-stat': 'opp_ft'}).text
					FTA = team.find('td', {'data-stat': 'opp_fta'}).text
					ORB = team.find('td', {'data-stat': 'opp_orb'}).text
					DRB = team.find('td', {'data-stat': 'opp_drb'}).text
					AST = team.find('td', {'data-stat': 'opp_ast'}).text
					STL = team.find('td', {'data-stat': 'opp_stl'}).text
					BLK = team.find('td', {'data-stat': 'opp_blk'}).text
					TOV = team.find('td', {'data-stat': 'opp_tov'}).text
					PF  = team.find('td', {'data-stat': 'opp_pf'}).text
					PTS = team.find('td', {'data-stat': 'opp_pts'}).text
					# o_team_shooting
					sql_query = "update o_team_shooting " \
								f"set o_team_fgm = {FG}, o_team_fga = {FGA}, o_team_3pm = {threeP}, " \
								f"o_team_3pa = {threePA}, o_team_ftm = {FT}, o_team_fta = {FTA} " \
								f"where team_name = '{name}'"
					cursor.execute(sql_query)
					connection.commit()
					# o_team_stats
					sql_query = "update o_team_stats " \
								f"set o_team_oreb = {ORB}, o_team_dreb = {DRB}, o_team_ast = {AST}, o_team_stl = {STL}, " \
								f"o_team_blk = {BLK}, o_team_tov = {TOV}, o_team_pf = {PF}, o_team_pts = {PTS} " \
								f"where team_name = '{name}'"
					cursor.execute(sql_query)
					connection.commit()
				
				current_time = datetime.datetime.now()
				current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
				sql_query = "delete from update_time"
				cursor.execute(sql_query)
				connection.commit()
				sql_query = f"insert into update_time values(\'{current_time_str}\')"
				cursor.execute(sql_query)
				connection.commit()
				print(f"Update successfully! @{current_time_str}")
				cursor.close()
				connection.close()
			except Exception as e:
				print(f"Error: {e}")
				return None
		else:
			print("Failed to fetch data from the website.")
	except Exception as e:
		print("An error occurred during update:", e)



def perform_update():
	print("Updating player info...")
	scrape_and_update()


scheduler = BackgroundScheduler()
scheduler.add_job(perform_update, 'interval', hours=1)
scheduler.start()
