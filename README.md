<div align="center">
	<img src="assets/icon.png" alt="Icon" width="150"/>
    <h1>Star Map Bot</h1>
    <p>
    	A simple and easy-to-use telegram bot that provides you with stargazing and astronomical information.
    </p>
</div>

[![CodeFactor](https://www.codefactor.io/repository/github/choitommy/star-map-bot/badge)](https://www.codefactor.io/repository/github/choitommy/star-map-bot)
[![Telegram Bot](https://img.shields.io/badge/Telegram-bot-blue?logo=telegram)](https://t.me/star_map_bot)

# Database Structure

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
        "telegram_user_id_1": {...},
        ...
    }
}
```

# Credits
- [Skyandtelescope](https://skyandtelescope.org)
- [WeatherAPI](https://www.weatherapi.com)
- [NASA SDO Data](https://sdo.gsfc.nasa.gov/data/)
- [Python telegram bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Google material icons](https://fonts.google.com/icons)