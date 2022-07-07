<div align="center">
	<img src="assets/icon.png" alt="Icon" width="150"/>
    <h1><span style="font-family: monospace;">astro* bot;</span></h1>
    <p>
    	A simple and easy-to-use telegram bot that provides you with stargazing and astronomical information.
    </p>
</div>

![Banner](assets/description_pic.png)
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

```jsonc
{
    "Users": {
        "telegram_user_id_0": {
            "latitude": 0,
            "longitude": 0,
            "address": "Your address",
            "username": "telegram_username_0",
            "utc_offset": 0,
            "creation_timestamp": "1970-01-01 00:00:00",
            "update_timestamp": "1970-01-01 00:00:00",
            "starmap_preferences": {    // default starmap preferences
                "showEquator": false,
                "showEcliptic": true,
                "showStarNames": false,
                "showPlanetNames": true,
                "showConsNames": true,
                "showConsLines": true,
                "showConsBoundaries": false,
                "showSpecials": false,
                "use24hClock": true
            },
        },
        // ...
    },
    "Subscriptions": {
        "telegram_user_id_0": {
            "telegram_chat_id_0": {     // chat_id == user_id for private chats
                "astrodata": {
                    "enabled": true, 
                    "timing": {
                        "hour": "19",   // default to UTC time if no location is set
                        "minute": "30"
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
        // ...
    },
}
```

## Credits
- [Skyandtelescope](https://skyandtelescope.org)
- [WeatherAPI](https://www.weatherapi.com)
- [NASA SDO Data](https://sdo.gsfc.nasa.gov/data/)
- [Python telegram bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Google material icons](https://fonts.google.com/icons)