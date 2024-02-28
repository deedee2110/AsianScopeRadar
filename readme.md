# AsianScope Radar Discord Bot
## Description
This discord bot is made to update the ATC Controller Status from VATSIM Public Data. It will update the status of the online controller and ATIS in the discord channel.

## Installation
1. Clone the repository
2. Install the required packages using pypi
```pip install -r requirements.txt```
3. Copy config.example.json to config.json and fill in the required information see Configuration section
4. Run the bot using
```python main.py``` or ```python3 main.py```

## Configuration
The configuration file is in JSON format. The file should be named config.json and should be in the same directory as the main.py file. The file should contain the following information:
```json
{
    "CONTROLLER_CHANNEL_ID" : 123456789,
    "ATIS_CHANNEL_ID" : 123456789,
    "CALLSIGN" : "2-LETTER ICAO CODE EG.VT,WS ",  
    "BOT_TOKEN" : "YOUR DISCORD BOT TOKEN"
}
```
## Usage
The bot will automatically update the status of the controller and ATIS in the specified channel. The bot will update the status every 1 minutes.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Software Used
- [Python](https://www.python.org/)
- [Discord.py](https://discordpy.readthedocs.io/en/stable/)
- [VATSIM Public Data API](https://data.vatsim.net/)
- [Requests](https://docs.python-requests.org/en/master/)

## Contributing
This is my very first python discord.py project, so any contribution is welcome. Please feel free to open an issue or a pull request.

