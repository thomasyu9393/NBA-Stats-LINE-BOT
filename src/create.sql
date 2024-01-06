create table team_code_to_name(
	team_code varchar,
	team_name varchar unique,
	primary key(team_code)
);

create table player_info(
	player_name varchar,
	pos varchar,
	age int,
	team_code varchar,
	player_gp int,
	player_min float,
	primary key(player_name),
	foreign key(team_code) references team_code_to_name(team_code)
);

create table team_info(
	team_name varchar,
	team_gp int,
	primary key(team_name),
	foreign key(team_name) references team_code_to_name(team_name)
);

create table player_shooting(
	player_name varchar,
	player_fgm float,
	player_fga float,
	player_3pm float,
	player_3pa float,
	player_ftm float,
	player_fta float,
	primary key(player_name),
	foreign key(player_name) references player_info
);

create table player_stats(
	player_name varchar,
	player_oreb float,
	player_dreb float,
	player_ast float,
	player_stl float,
	player_blk float,
	player_tov float,
	player_pf float,
	player_pts float,
	primary key(player_name),
	foreign key(player_name) references player_info
);

create table team_shooting(
	team_name varchar,
	team_fgm float,
	team_fga float,
	team_3pm float,
	team_3pa float,
	team_ftm float,
	team_fta float,
	primary key(team_name),
	foreign key(team_name) references team_info
);

create table team_stats(
	team_name varchar,
	team_oreb float,
	team_dreb float,
	team_ast float,
	team_stl float,
	team_blk float,
	team_tov float,
	team_pf float,
	team_pts float,
	primary key(team_name),
	foreign key(team_name) references team_info
);

create table o_team_shooting(
	team_name varchar,
	o_team_fgm float,
	o_team_fga float,
	o_team_3pm float,
	o_team_3pa float,
	o_team_ftm float,
	o_team_fta float,
	primary key(team_name),
	foreign key(team_name) references team_info
);

create table o_team_stats(
	team_name varchar,
	o_team_oreb float,
	o_team_dreb float,
	o_team_ast float,
	o_team_stl float,
	o_team_blk float,
	o_team_tov float,
	o_team_pf float,
	o_team_pts float,
	primary key(team_name),
	foreign key(team_name) references team_info
);

create table update_time(
	upd_time varchar,
	primary key(upd_time)
);