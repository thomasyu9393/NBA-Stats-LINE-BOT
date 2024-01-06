from app import line_bot_api, handler, prediction
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import StickerMessage, StickerSendMessage
import configparser
import psycopg2
import numpy as np

config = configparser.ConfigParser()
config.read('config.ini')

DB_HOST = config.get('database', 'DB_HOST')
DB_PORT = config.getint('database', 'DB_PORT')
DB_USER = config.get('database', 'DB_USER')
DB_PASSWORD = config.get('database', 'DB_PASSWORD')
DB_NAME = config.get('database', 'DB_NAME')

def get_player_info(player_name):
	player_name = player_name.replace("'", "''")
	try:
		connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
		with connection.cursor() as cursor:
			sql_query = "select player_info.player_name, team_name, pos, age, player_gp, player_pts, player_oreb + player_dreb as player_reb, player_ast, " \
			"player_stl, player_blk, player_tov, player_pf, player_fgm / player_fga as player_fg, player_3pm / player_3pa as player_3p, " \
			"player_ftm / player_fta as player_ft " \
			"from player_info natural join player_stats natural join player_shooting natural join team_code_to_name " \
			f"where player_info.player_name = '{player_name}'"
			cursor.execute(sql_query)
			player_info = cursor.fetchone()
			return player_info
	except Exception as e:
		print(f"Error: {e}")
		return None
	finally:
		if connection:
			connection.close()


def get_team_info(team_code):
	try:
		connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
		with connection.cursor() as cursor:
			sql_query = "select team_name, team_gp, team_pts, team_oreb + team_dreb as team_reb, team_ast, " \
			"team_stl, team_blk, team_tov, team_pf, team_fgm / team_fga as team_fg, team_3pm / team_3pa as team_3p, " \
			"team_ftm / team_fta as team_ft " \
			"from team_info natural join team_stats natural join team_shooting natural join team_code_to_name " \
			f"where team_code = '{team_code}' or team_name like '% {team_code}'"
			cursor.execute(sql_query)
			team_info = cursor.fetchone()
			return team_info
	except Exception as e:
		print(f"Error: {e}")
		return None
	finally:
		if connection:
			connection.close()


def get_team_info_full(team_code):
	try:
		connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
		with connection.cursor() as cursor:
			#fga, fgm/fga, 3pa, 3pm/3pa, fta, ftm/fta, oreb, dreb, ast, stl, blk, tov, pf, pts
			sql_query = "select team_fga, team_fgm / team_fga, team_3pa, team_3pm / team_3pa, team_fta, team_ftm / team_fta, " \
			       		"team_oreb, team_dreb, team_ast, team_stl, team_blk, team_tov, team_pf, team_pts " \
						"from team_stats natural join team_shooting natural join team_code_to_name " \
						f"where team_code = '{team_code}' or team_name like '% {team_code}'"
			cursor.execute(sql_query)
			team_info = cursor.fetchone()
			return team_info
	except Exception as e:
		print(f"Error: {e}")
		return None
	finally:
		if connection:
			connection.close()


def get_oppo_info(team_code):
	try:
		connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
		with connection.cursor() as cursor:
			#ofga, ofgm/ofga, o3pa, o3pm/o3pa, ofta, oftm/ofta, ooreb, odreb, oast, ostl, oblk, otov, opf, opts
			sql_query = "select o_team_fga, o_team_fgm / o_team_fga, o_team_3pa, o_team_3pm / o_team_3pa, o_team_fta, o_team_ftm / o_team_fta, " \
			       		"o_team_oreb, o_team_dreb, o_team_ast, o_team_stl, o_team_blk, o_team_tov, o_team_pf, o_team_pts " \
						"from o_team_stats natural join o_team_shooting natural join team_code_to_name " \
						f"where team_code = '{team_code}' or team_name like '% {team_code}'"
			cursor.execute(sql_query)
			team_info = cursor.fetchone()
			return team_info
	except Exception as e:
		print(f"Error: {e}")
		return None
	finally:
		if connection:
			connection.close()


def get_team_name(team_code):
	try:
		connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
		with connection.cursor() as cursor:
			sql_query = "select team_name from team_code_to_name " \
						f"where team_code = '{team_code}' or team_name like '% {team_code}'"
			cursor.execute(sql_query)
			team_info = cursor.fetchone()
			return team_info[0]
	except Exception as e:
		print(f"Error: {e}")
		return None
	finally:
		if connection:
			connection.close()


def read_last_update_time():
	try:
		connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
		with connection.cursor() as cursor:
			sql_query = "select * from update_time"
			cursor.execute(sql_query)
			upd_time = cursor.fetchone()
			return upd_time[0] + " (UTC+0)"
	except Exception as e:
		print(f"Error: {e}")
		return 'Error'
	finally:
		if connection:
			connection.close()


def sigmoid(x):
	return 1 / (1 + np.exp(-x))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	user_message = event.message.text.split(',')
	user_message[0] = user_message[0].lower()

	if "player" in user_message[0]:
		if len(user_message) == 2:
			player_name = user_message[1].strip()
			player_info = get_player_info(player_name)
			if player_info:
				last_upd_time = read_last_update_time()
				response_message = "Player Info:\n=====\n" \
				f"Name: {player_info[0]}\n" \
				f"Team: {player_info[1]}\n" \
				f"POS: {player_info[2]}\n" \
				f"Age: {player_info[3]}\n" \
				f"GP: {player_info[4]}\n" \
				f"PTS: {player_info[5]}\n" \
				f"REB: {round(player_info[6], 1)}\n" \
				f"AST: {player_info[7]}\n" \
				f"STL: {player_info[8]}\n" \
				f"BLK: {player_info[9]}\n" \
				f"TOV: {player_info[10]}\n" \
				f"PF: {player_info[11]}\n" \
				f"FG%: {round(player_info[12] * 100, 1)}\n" \
				f"3P%: {round(player_info[13] * 100, 1)}\n" \
				f"FT%: {round(player_info[14] * 100, 1)}\n" \
				f"=====\nLast Updated @{last_upd_time}"
				reply_message(event, response_message)
			else:
				response_message = "Player not found."
				reply_message(event, response_message)
		else:
			response_message = "Wrong format to search for a single player."
			reply_message(event, response_message)
	elif "team" in user_message[0]:
		if len(user_message) == 2:
			team_code = user_message[1].strip()
			team_info = get_team_info(team_code)
			if team_info:
				last_upd_time = read_last_update_time()
				response_message = "Team Info:\n=====\n" \
				f"Team: {team_info[0]}\n" \
				f"GP: {team_info[1]}\n" \
				f"PTS: {team_info[2]}\n" \
				f"REB: {round(team_info[3], 1)}\n" \
				f"AST: {team_info[4]}\n" \
				f"STL: {team_info[5]}\n" \
				f"BLK: {team_info[6]}\n" \
				f"TOV: {team_info[7]}\n" \
				f"PF: {team_info[8]}\n" \
				f"FG%: {round(team_info[9] * 100, 1)}\n" \
				f"3P%: {round(team_info[10] * 100, 1)}\n" \
				f"FT%: {round(team_info[11] * 100, 1)}\n" \
				f"=====\nLast Updated @{last_upd_time}"
				reply_message(event, response_message)
			else:
				response_message = f"Team not found. Query: {team_code}"
				reply_message(event, response_message)
		else:
			response_message = "Wrong format to search for a single team."
			reply_message(event, response_message)
	elif "lottery" in user_message[0]:
		if len(user_message) == 3:
			team_1_code = user_message[1].strip()
			team_1 = get_team_name(team_1_code)
			team_1_info = get_team_info_full(team_1_code)
			team_1_oppo = get_oppo_info(team_1_code)
			team_2_code = user_message[2].strip()
			team_2 = get_team_name(team_2_code)
			team_2_info = get_team_info_full(team_2_code)
			team_2_oppo = get_oppo_info(team_2_code)
			last_upd_time = read_last_update_time()
			if team_1_info and team_2_info:
				pred = prediction.get_prediction(team_1_info + team_2_oppo, team_2_info + team_1_oppo)
				if (pred[0] >= pred[1]):
					prob = sigmoid((pred[0] - pred[1]) / 15)
					response_message = f"Lottery Result:\n=====\n{team_1} will win with probability {round(prob * 100, 2)}%,\n" \
										f"and will get {round(pred[0] - pred[1])} more points than {team_2}.\n\n" \
										f"Two teams will score between ({round(pred[0] + pred[1]) - 2.5}, {round(pred[0] + pred[1]) + 2.5}) points combined.\n" \
										f"=====\nLast Updated @{last_upd_time}"
					reply_message(event, response_message)
				else:
					prob = sigmoid((pred[1] - pred[0]) / 15)
					response_message = f"Lottery Result:\n=====\n{team_2} will win with probability {round(prob * 100, 2)}%,\n" \
										f"and will get {round(pred[1] - pred[0])} more points than {team_1}.\n\n" \
										f"Two teams will score between ({round(pred[0] + pred[1]) - 2.5}, {round(pred[0] + pred[1]) + 2.5}) points combined.\n" \
										f"=====\nLast Updated @{last_upd_time}"
					reply_message(event, response_message)
			elif team_1_info:
				response_message = f"Team {team_2_code} not found."
				reply_message(event, response_message)
			else:
				response_message = f"Team {team_1_code} not found."
				reply_message(event, response_message)
		else:
			response_message = "Wrong format for the lottery!"
			reply_message(event, response_message)
	else:
		response_message = "Please enter keywords separate by comma:\n\n" \
							"\"player, <a player name>\"\n>> Search for a player info.\n>> e.g. \"player, Stephen Curry\"\n\n" \
							"\"team, <a team code or name>\"\n>> Search for a team info.\n>> e.g. \"team, GSW\" or \"team, Warriors\"\n\n" \
							"\"lottery, <team 1 code or name>, <team 2 code or name>\"\n>>"
		reply_message(event, response_message)


def reply_message(event, text):
	line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
	sticker_message = event.message
	sticker_package_id = sticker_message.package_id
	sticker_id = sticker_message.sticker_id

	line_bot_api.reply_message(
		event.reply_token,
		StickerSendMessage(package_id=sticker_package_id, sticker_id=sticker_id)
	)