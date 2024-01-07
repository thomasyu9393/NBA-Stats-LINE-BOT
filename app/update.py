import requests
from bs4 import BeautifulSoup
import configparser
import psycopg2
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import csv

config = configparser.ConfigParser()
config.read('config.ini')

DB_HOST = config.get('database', 'DB_HOST')
DB_PORT = config.getint('database', 'DB_PORT')
DB_USER = config.get('database', 'DB_USER')
DB_PASSWORD = config.get('database', 'DB_PASSWORD')
DB_NAME = config.get('database', 'DB_NAME')

def get_player():
	try:
		url = 'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'
		response = requests.get(url)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			players = soup.find('table', {'id': 'per_game_stats'}).find('tbody').find_all('tr', {'class': 'full_table'})

			modified_players = []
			for player in players:
				modified_player = {
					'name': player.find('td', {'data-stat': 'player'}).text,
					'position': player.find('td', {'data-stat': 'pos'}).text,
					'age':     player.find('td', {'data-stat': 'age'}).text,
					'team_id': player.find('td', {'data-stat': 'team_id'}).text,
					'GP':      player.find('td', {'data-stat': 'g'}).text,
					'MinP':    player.find('td', {'data-stat': 'mp_per_g'}).text,
					'FG':      player.find('td', {'data-stat': 'fg_per_g'}).text,
					'FGA':     player.find('td', {'data-stat': 'fga_per_g'}).text,
					'threeP':  player.find('td', {'data-stat': 'fg3_per_g'}).text,
					'threePA': player.find('td', {'data-stat': 'fg3a_per_g'}).text,
					'FT':  player.find('td', {'data-stat': 'ft_per_g'}).text,
					'FTA': player.find('td', {'data-stat': 'fta_per_g'}).text,
					'ORB': player.find('td', {'data-stat': 'orb_per_g'}).text,
					'DRB': player.find('td', {'data-stat': 'drb_per_g'}).text,
					'AST': player.find('td', {'data-stat': 'ast_per_g'}).text,
					'STL': player.find('td', {'data-stat': 'stl_per_g'}).text,
					'BLK': player.find('td', {'data-stat': 'blk_per_g'}).text,
					'TOV': player.find('td', {'data-stat': 'tov_per_g'}).text,
					'PF':  player.find('td', {'data-stat': 'pf_per_g'}).text,
					'PTS': player.find('td', {'data-stat': 'pts_per_g'}).text
				}
				modified_players.append(modified_player)

			name_count = {}
			for player in modified_players:
				name_count[player['name']] = name_count.get(player['name'], 0) + 1
			multiple = [name for name, count in name_count.items() if count > 1]
			res = [player for player in modified_players if (player['name'] not in multiple) or (player['position'] == 'TOT')]

			return res
		else:
			print("Failed to fetch data from the website 1.")
			return None
	except Exception as e:
		print("An error occurred during \"get_player()\":", e)


def get_team():
	try:
		url = 'https://www.basketball-reference.com/leagues/NBA_2024.html'
		response = requests.get(url)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			teams = soup.find('table', {'id': 'per_game-team'}).find('tbody').find_all('tr')

			modified_teams = []
			for team in teams:
				modified_team = {
					'name': team.find('td', {'data-stat': 'team'}).text.replace("'", "''"),
					'GP':      team.find('td', {'data-stat': 'g'}).text,
					'FG':      team.find('td', {'data-stat': 'fg'}).text,
					'FGA':     team.find('td', {'data-stat': 'fga'}).text,
					'threeP':  team.find('td', {'data-stat': 'fg3'}).text,
					'threePA': team.find('td', {'data-stat': 'fg3a'}).text,
					'FT':  team.find('td', {'data-stat': 'ft'}).text,
					'FTA': team.find('td', {'data-stat': 'fta'}).text,
					'ORB': team.find('td', {'data-stat': 'orb'}).text,
					'DRB': team.find('td', {'data-stat': 'drb'}).text,
					'AST': team.find('td', {'data-stat': 'ast'}).text,
					'STL': team.find('td', {'data-stat': 'stl'}).text,
					'BLK': team.find('td', {'data-stat': 'blk'}).text,
					'TOV': team.find('td', {'data-stat': 'tov'}).text,
					'PF':  team.find('td', {'data-stat': 'pf'}).text,
					'PTS': team.find('td', {'data-stat': 'pts'}).text
				}
				modified_teams.append(modified_team)

			return modified_teams
		else:
			print("Failed to fetch data from the website 2.")
			return None
	except Exception as e:
		print("An error occurred during \"get_team()\":", e)


def get_opp_team():
	try:
		url = 'https://www.basketball-reference.com/leagues/NBA_2024.html'
		response = requests.get(url)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			opp_teams = soup.find('table', {'id': 'per_game-opponent'}).find('tbody').find_all('tr')
			modified_teams = []
			for team in opp_teams:
				modified_team = {
					'name': team.find('td', {'data-stat': 'team'}).text.replace("'", "''"),
					'FG':      team.find('td', {'data-stat': 'opp_fg'}).text,
					'FGA':     team.find('td', {'data-stat': 'opp_fga'}).text,
					'threeP':  team.find('td', {'data-stat': 'opp_fg3'}).text,
					'threePA': team.find('td', {'data-stat': 'opp_fg3a'}).text,
					'FT':  team.find('td', {'data-stat': 'opp_ft'}).text,
					'FTA': team.find('td', {'data-stat': 'opp_fta'}).text,
					'ORB': team.find('td', {'data-stat': 'opp_orb'}).text,
					'DRB': team.find('td', {'data-stat': 'opp_drb'}).text,
					'AST': team.find('td', {'data-stat': 'opp_ast'}).text,
					'STL': team.find('td', {'data-stat': 'opp_stl'}).text,
					'BLK': team.find('td', {'data-stat': 'opp_blk'}).text,
					'TOV': team.find('td', {'data-stat': 'opp_tov'}).text,
					'PF':  team.find('td', {'data-stat': 'opp_pf'}).text,
					'PTS': team.find('td', {'data-stat': 'opp_pts'}).text
				}
				modified_teams.append(modified_team)

			return modified_teams
		else:
			print("Failed to fetch data from the website 3.")
			return None
	except Exception as e:
		print("An error occurred during \"get_opp_team()\":", e)


def scrape_and_update():
	players = get_player()
	if players is not None:
		try:
			connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
			cursor = connection.cursor()
			for player in players:
				player['name'] = player['name'].replace("'", "''")
				# player_shooting
				sql_query = "update player_shooting " \
							f"set player_fgm = {player['FG']}, player_fga = {player['FGA']}, player_3pm = {player['threeP']}, " \
							f"player_3pa = {player['threePA']}, player_ftm = {player['FT']}, player_fta = {player['FTA']} " \
							f"where player_name = '{player['name']}'"
				cursor.execute(sql_query)
				connection.commit()
				# player_stats
				sql_query = "update player_stats " \
							f"set player_oreb = {player['ORB']}, player_dreb = {player['DRB']}, player_ast = {player['AST']}, player_stl = {player['STL']}, " \
							f"player_blk = {player['BLK']}, player_tov = {player['TOV']}, player_pf = {player['PF']}, player_pts = {player['PTS']} " \
							f"where player_name = '{player['name']}'"
				cursor.execute(sql_query)
				connection.commit()
				# player_info
				sql_query = "update player_info " \
							f"set pos = '{player['position']}', age = {player['age']}, team_code = '{player['team_id']}', player_gp = {player['GP']}, player_min = {player['MinP']} " \
							f"where player_name = '{player['name']}'"
				cursor.execute(sql_query)
				connection.commit()

			teams = get_team()
			for team in teams:
				# team_shooting
				sql_query = "update team_shooting " \
							f"set team_fgm = {team['FG']}, team_fga = {team['FGA']}, team_3pm = {team['threeP']}, " \
							f"team_3pa = {team['threePA']}, team_ftm = {team['FT']}, team_fta = {team['FTA']} " \
							f"where team_name = '{team['name']}'"
				cursor.execute(sql_query)
				connection.commit()
				# team_stats
				sql_query = "update team_stats " \
							f"set team_oreb = {team['ORB']}, team_dreb = {team['DRB']}, team_ast = {team['AST']}, team_stl = {team['STL']}, " \
							f"team_blk = {team['BLK']}, team_tov = {team['TOV']}, team_pf = {team['PF']}, team_pts = {team['PTS']} " \
							f"where team_name = '{team['name']}'"
				cursor.execute(sql_query)
				connection.commit()
				# team_info
				sql_query = "update team_info " \
							f"set team_gp = '{team['GP']}' " \
							f"where team_name = '{team['name']}'"
				cursor.execute(sql_query)
				connection.commit()

			opp_teams = get_opp_team()
			for team in opp_teams:
				# o_team_shooting
				sql_query = "update o_team_shooting " \
							f"set o_team_fgm = {team['FG']}, o_team_fga = {team['FGA']}, o_team_3pm = {team['threeP']}, " \
							f"o_team_3pa = {team['threePA']}, o_team_ftm = {team['FT']}, o_team_fta = {team['FTA']} " \
							f"where team_name = '{team['name']}'"
				cursor.execute(sql_query)
				connection.commit()
				# o_team_stats
				sql_query = "update o_team_stats " \
							f"set o_team_oreb = {team['ORB']}, o_team_dreb = {team['DRB']}, o_team_ast = {team['AST']}, o_team_stl = {team['STL']}, " \
							f"o_team_blk = {team['BLK']}, o_team_tov = {team['TOV']}, o_team_pf = {team['PF']}, o_team_pts = {team['PTS']} " \
							f"where team_name = '{team['name']}'"
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
			print(f"Error at \"scrape_and_update()\": {e}")
			return None
	else:
		print("Failed to fetch data from the website.")


def perform_update():
	print("Updating the database...")
	scrape_and_update()


def initialize_db():
	try:
		connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
		cursor = connection.cursor()
		cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'team_code_to_name')")
		table_exists = cursor.fetchone()[0]
		if not table_exists:
			with open('src/create.sql', 'r') as sql_file:
				sql_commands = sql_file.read()
				cursor.execute(sql_commands)
				connection.commit()
				print("Creating tables SQL are excuted.")

			with open('src/TEAM_CODE_TO_NAME.csv', 'r', newline='') as file:
				reader = csv.DictReader(file)
				for row in reader:
					code = row['Code']
					team = row['Team']
					cursor.execute("INSERT INTO team_code_to_name (team_code, team_name) VALUES (%s, %s)", (code, team))
				print("Code to Name are inserted.")
				connection.commit()
			
			players = get_player()
			for player in players:
				# player_info
				sql_query = "INSERT INTO player_info (player_name, pos, age, team_code, player_gp, player_min) VALUES (%s, %s, %s, %s, %s, %s)"
				cursor.execute(sql_query, (player['name'], player['position'], player['age'], player['team_id'], player['GP'], player['MinP']))
				connection.commit()
				# player_shooting
				sql_query = "INSERT INTO player_shooting (player_name, player_fgm, player_fga, player_3pm, player_3pa, player_ftm, player_fta) VALUES (%s, %s, %s, %s, %s, %s, %s)"
				cursor.execute(sql_query, (player['name'], player['FG'], player['FGA'], player['threeP'], player['threePA'], player['FT'], player['FTA']))
				connection.commit()
				# player_stats
				sql_query = "INSERT INTO player_stats (player_name, player_oreb, player_dreb, player_ast, player_stl, player_blk, player_tov, player_pf, player_pts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
				cursor.execute(sql_query, (player['name'], player['ORB'], player['DRB'], player['AST'], player['STL'], player['BLK'], player['TOV'], player['PF'], player['PTS']))
				connection.commit()
			print("Player info are inserted.")

			teams = get_team()
			for team in teams:
				# team_info
				sql_query = "INSERT INTO team_info (team_name, team_gp) VALUES (%s, %s)"
				cursor.execute(sql_query, (team['name'], team['GP']))
				connection.commit()
				# team_shooting
				sql_query = "INSERT INTO team_shooting (team_name, team_fgm, team_fga, team_3pm, team_3pa, team_ftm, team_fta) VALUES (%s, %s, %s, %s, %s, %s, %s)"
				cursor.execute(sql_query, (team['name'], team['FG'], team['FGA'], team['threeP'], team['threePA'], team['FT'], team['FTA']))
				connection.commit()
				# team_stats
				sql_query = "INSERT INTO team_stats (team_name, team_oreb, team_dreb, team_ast, team_stl, team_blk, team_tov, team_pf, team_pts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
				cursor.execute(sql_query, (team['name'], team['ORB'], team['DRB'], team['AST'], team['STL'], team['BLK'], team['TOV'], team['PF'], team['PTS']))
				connection.commit()
			print("Team info are inserted.")

			opp_teams = get_opp_team()
			for team in opp_teams:
				# o_team_shooting
				sql_query = "INSERT INTO o_team_shooting (team_name, o_team_fgm, o_team_fga, o_team_3pm, o_team_3pa, o_team_ftm, o_team_fta) VALUES (%s, %s, %s, %s, %s, %s, %s)"
				cursor.execute(sql_query, (team['name'], team['FG'], team['FGA'], team['threeP'], team['threePA'], team['FT'], team['FTA']))
				connection.commit()
				# o_team_stats
				sql_query = "INSERT INTO o_team_stats (team_name, o_team_oreb, o_team_dreb, o_team_ast, o_team_stl, o_team_blk, o_team_tov, o_team_pf, o_team_pts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
				cursor.execute(sql_query, (team['name'], team['ORB'], team['DRB'], team['AST'], team['STL'], team['BLK'], team['TOV'], team['PF'], team['PTS']))
				connection.commit()
			print("Opponent Team info are inserted.")

			current_time = datetime.datetime.now()
			current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
			sql_query = f"insert into update_time values(\'{current_time_str}\')"
			cursor.execute(sql_query)
			connection.commit()
			print(f"ALL info are inserted successfully! @{current_time_str}")
		else:
			print("Tables are already exist.")
			perform_update()
		cursor.close()
		connection.close()
	except Exception as e:
		print(f"Error at \"initialize_db()\": {e}")
		return None



initialize_db()

scheduler = BackgroundScheduler()
scheduler.add_job(perform_update, 'interval', hours=1)
scheduler.start()

while True:
	pass