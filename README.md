<div align="center">
	<img src="assets/icon.png" alt="Icon" width="150"/>
    <h1><code>astro* bot;</code></h1>
    <p>
    	A simple and easy-to-use telegram bot that provides you with stargazing and astronomical information.
    </p>
</div>

[![CodeFactor](https://www.codefactor.io/repository/github/choitommy/astro-pointer-bot/badge)](https://www.codefactor.io/repository/github/choitommy/astro-pointer-bot)
[![Telegram Bot](https://img.shields.io/badge/Telegram-bot-blue?logo=telegram)](https://t.me/AstroPointerBot)

## Introduction
WIP

## Features

| Command         	            | Function 	|
|---------------------------	|----------	|
| `/start`                  	| -        	|
| `/starmap`                	| -        	|
| `/astrodata`              	| -        	|
| `/weather`            	    | -        	|
| `/sun`                 	    | -        	|
| `/iss`                	    | -        	|
| `/subscribe` (or `/sub`)      | -        	|
| `/unsubscribe` (or `/unsub`)  | -        	|
| `/myinfo`             	    | -        	|
| `/deletemyinfo`       	    | -        	|
| `/setlocation`        	    | -        	|
| `/cancel`             	    | -        	|
| `/credits`            	    | -        	|

## Database Structure

```json
{
    "Users": {
        "telegram_user_id_0": {
            "latitude": 0,
            "longitude": 0,
            "address": "Your address",
            "username": "telegram_username_0",
            "utcOffset": 0,
            "creation_timestamp": "1970-01-01 00:00:00",
            "update_timestamp": "1970-01-01 00:00:00",
        },
    },
    "Subscriptions": {
        "telegram_user_id_0": {
            "telegram_chat_id_0": {     // users can have different subscriptions in both bot's DM and groups
                "astrodata": {
                    "enabled": true, 
                    "timing": {
                        "hour": "19",   // in accordance with the `utcOffset` above, 
                        "minute": "30"  // defaults to UTC time if not set up
                    }
                },
                "iss": {
                    "enabled": false, 
                    "timing": {
                        "hour": "-1", 
                        "minute": "-1"
                    }
                },
                "starmap": {
                    "enabled": true, 
                    "timing": {
                        "hour": "00", 
                        "minute": "05"
                    }
                },
                "sun": {
                    "enabled": false, 
                    "timing": {
                        "hour": "-1", 
                        "minute": "-1"
                    }
                },
                "weather": {
                    "enabled": false, 
                    "timing": {
                        "hour": "-1", 
                        "minute": "-1"
                    }
                },
            },
        },
    },
}
```

## Credits
- [Skyandtelescope](https://skyandtelescope.org)
- [WeatherAPI](https://www.weatherapi.com)
- [NASA SDO Data](https://sdo.gsfc.nasa.gov/data/)
- [Python telegram bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Google material icons](https://fonts.google.com/icons)