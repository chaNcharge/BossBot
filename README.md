# BossBot
This is a discord bot that was made to help manage Human Resources. It was made as a proof of concept and to be helpful for discord moderators. Our hope are to eventually make this a more polished version for Slack and professional setting.

## BossBot Functionality

BossBot function was to help with scheduling and personnel records and helping with timely clock in and Quick and easy check for regional holidays to prevent time theft.

## Commands

* `!ping`: test if there is a connection
* `!echo`: Test to see if sever is active
* `!register`: takes user name, birthday, and region to store into a data base for later reference.
* `!today`: Shows a quote of the day and the users schedule for the day Checks for  user birthday and region holidays to see if the user has work today.
* `!schedule`: the has the user input their weekly schedule by days of the week to store into a data base for later reference.
* `!check_work`: This command is a Passive checks to see if the user is online and punched in and also punched out at end of day.
* `!work_schedule`: User inputs a date and then the bot will show if they have work on that day.
 
## How to set up
0. Install python 3
1. Download or clone the repository
2. Copy `config.json.example` as `config.json`
3. Insert your bots token from https://discord.com/developers/applications into the `token` field
4. Run `pip install -r requirements.txt` to install required packages
5. Run `python bot.py`


## Authors
Ethan Cha, Daniel Willard