# NBA-Stats-LINE-BOT
The final project for *Intro. to Database Systems*, 2023 Fall.

A LINE BOT deployed on Heroku, using AWS RDS instance.

All stats referenced from <https://www.basketball-reference.com/> in season 2023-24.

## Configuration
1. Create a LINE BOT
	- Get the CHANNEL ACCESS TOKEN
	- Get the CHANNEL SECRET
2. Create an AWS RDS PostgreSQL database
	- Get the database endpoint
	- Get the port
	- Set the parameter in `config.ini`
	- Set the VPC security group's inbound/outbound rule with ALL TRAFFIC to ANY IPv4 address `0.0.0.0`
3. Create a HEROKU project
	- `git init` under the cloned repo dir
	- `heroku git:remote -a <the name of HEROKU project>`
	- `git push heroku master` the whole to deploy
4. LINE BOT Webhook setting
	- Set Webhook URL as `https://<>.herokuapp.com/callback`
	- Add reply bot as your LINE friend and start to explore!
5. First setup
    - The program will **automatically create all the tables needed** in the database, and also perform the data scrapping to insert data into the database.
    - There is also an auto-update mechanism, please reference the section `Auto-Update` below.

## Functionality
- The welcome message:
```
Please enter keywords seperate by comma:

"player, <a player name>"
>> Search for a player info.
>> e.g. "player, Stephen Curry"

"team, <a team code or name>"
>> Search for a team info.
>> e.g. "team, GSW" or "team, Warriors"

"lottery, <team 1 code or name>, <team 2 code or name>"
>> Get prediction on the match.
>> e.g. "lottery, Rockets, GSW"
```
There is a correspondence table between team codes and team names at `./src/TEAM_CODE_TO_NAME.csv`
- Query a player info
    - Reference <https://www.basketball-reference.com/leagues/NBA_2024_per_game.html>
    - You will get the current stats of that player including:
        - Team
        - Age
        - Game Played
        - Points per Game (and the following)
        - Total Rebounds
        - Assists
        - Steals
        - Blocks
        - Turnovers
        - Personal Fouls
        - Field Goal Percentage
        - 3-Point Field Goal Percentage
        - Free Throw Percentage
- Query a team info
    - Reference <https://www.basketball-reference.com/leagues/NBA_2024.html>
    - You will get the team stats similar to player stats.
- Play the lottery!
    - Given two teams, you get which team will win with what probability, the point difference, and the estimated range of combined score points.

## Auto-Update
- Use `requests` and `BeautifulSoup` to scrap the web page.
- Currently, the data in the database will be updated every 1 hour.
- During the update session, **you can still perform query without any effect.**
- For each query, you will get the last update time for your reference.

## SQL Query
- Use `psycopg2` to perform all the SQL query including:
    - `CREATE TABLE`
    - `INSERT INTO`
    - `SELECT FROM WHERE`
    - `UPDATE SET WHERE`

## Prediction
With the training data from the last two seasons (21-22, 22-23) statistics, we trained the model via `tensorflow` and generated `.keras` files. However, Heroku doesn't support installing `tensorflow`, so we trained the model again by `scikit learn` to get `.pkl` files. It is now available to get the prediction of the match by our models.

## Misc.
- We can handle the player name with special characters, such as `D'Angelo Russell` or `Alperen Şengün`.
- If a player is traded to another team in season 2023-24, then the stats of that player will be treated as the total stats at all the teams.
- If you send a sticker to the LINE BOT, then it will reply to you the same sticker. (Only official or default stickers)
