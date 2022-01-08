<div align="center">
  <img src="https://i.imgur.com/sxfp0vX.png" height="300" align="center">
  <br>
  <p>Plexy connects your plex server to your discord server. 
    By sending messages to a certain discord channel when new content is added. 
    And enabling users to look trough and get info about the plex server.
    </p> 
  <br>
    <img src="https://img.shields.io/badge/Plexy-v6.0.0-orange?style=for-the-badge&logo=discord" alt="Support">
  <br>
  <br>
<br>
    <a href="https://github.com/CecilioSilva/Plexy/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/CecilioSilva/Plexy?style=for-the-badge"></a>
    <a href="https://github.com/CecilioSilva/Plexy/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/CecilioSilva/Plexy?style=for-the-badge"></a>
    <a href="https://ko-fi.com/gamingismyfood"><img alt="Sponsor Link" src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white"></a>
    <a href="https://github.com/CecilioSilva/Plexy/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/CecilioSilva/Plexy?style=for-the-badge"></a>
    <a href="https://github.com/CecilioSilva/Plexy/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/CecilioSilva/Plexy?style=for-the-badge"></a>
</div>

---
<div align="center">
    <img src="https://i.imgur.com/Abn4f91.png" align="center" style="weight: 500px"/>
</div>

---
# Features ✨

Plexy is a one of a kind discord bot

- Easy to use ⚒️
- Easy to configure ⚙️
- Customizable 📐
- Two different modes
---

## How to use Plexy 🤖
### Requirements 📜

- [Python](https://www.python.org/downloads/) 3.6 or Higher (I used 3.9)
- A Plex admin account
- Discord account
- [Latest release](https://github.com/CecilioSilva/Plexy/releases/latest)

---

##### 1. Make your own discord bot

First go to the [Discord Developer Portal](https://discord.com/developers/applications/)
login with your discord account
press `new application`
type the application name and press `Create`
set your application/bot icon and description/about me
choose form the navbar in the left `Bot` option
press `add bot` and `yes, do it!`

##### 2. make sure you have [Python 3.6 or higher](https://www.python.org/downloads/) installed

##### 3. Download [latest release](https://github.com/CecilioSilva/Plexy/releases/latest)

##### 4. Login to plex with an admin account

##### 5. Unzip the source files and locate `configs/secrets.example.json` it should look like this:

```json
{
  "bot_token": "<Bot Token>",
  "notificationsChannelId": 1000000000000000000,
  "plexAdminDiscordId": 1000000000000000000,
  "plexBaseUrl": "<Plex Base Url>",
  "plexToken": "<Plex X-Token>",
  "contentUrl": "<Plex Content URL>"
}
```

- `bot_token` &#8594; The discord bot token you can find in the [Discord developer portal](https://discord.com/developers/applications/)  
- `notificationChannelid` &#8594; Go to discord client `Settings` > `Advanced` > `Developer Mode` and enable it. Then go to the channel you want the new content notifications and right click it and `Copy ID`  
- `plexAdminDiscordId` &#8594; Do the same as `notificationChannelid` but select the discord user you that controls the plex server
- `plexBaseUrl` &#8594; Go to [Plex](https://www.plex.tv/) and open the dashboard. goto `Settings` > `Remote Access` if plex server is on the same system as the bot use `http://localhost:32400/`, otherwise use the public ip and port
- `plexToken` &#8594; See [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
- `contentUrl` &#8594; Go to the [Plex](https://www.plex.tv/) Dashboard and open a media item. then in the address-bar copy everything until `/details`  
  ![Content-url](https://i.imgur.com/iL1Bl6S.png)

##### 6. Rename the file to `secrets.json`

##### 7. Open `configs/config.example.json`

```json
  "plex_config": {
    "refreshTime": 15,
    "max-recently-added": 20,
    "scanLibraries": ["TV Shows", "Movies", "Anime"],
    "allLibraries": ["Anime", "Movies", "Home videos", "TV Shows"]
  }
```
- `scanLibraries` &#8594; Are all the libraries Plexy searches for new content
- `allLibraries` &#8594; All the libraries you want plexy to see

```json
"args": {
  "-all": ["Anime", "Movies", "TV Shows"],
  "-movie": ["Movies"],
  "-m": ["Movies"],
  "-show": ["TV Shows"],
  "-s": ["TV Shows"],
  "-anime": ["Anime"],
  "-a": ["Anime"],
  "-h": ["Home videos"],
  "-videos": ["Videos"],
  "-v": ["Videos"]
}
```
These are all the flags users can use to filter for libraries
you can add and remove any flag you want


#### 8. Choose if you want safe mode or not


| :exclamation:  This is very important   |
|-----------------------------------------|

```json
  "general_config" : {
    "safe-mode": true
  }
```

**🛑 Plexy uses the plex token to get media assets from the plex server. 
But that exposes the plex token you have set to everybody in the discord server/channel. 🛑**
         



#### 9. Rename the file to `config.json`

---

## Run The Project 🌀

To run the project

0. (Optional) Make a [virtual environment](https://docs.python.org/3/library/venv.html)
1. Install all the dependencies
    ```commandline
        pip install -r requirements.txt
    ```

2. Run the bot
    ```commandline
        python Bot.py
    ```

## Sponsor
Plexy is free and will always be free to use. I did spend a lot of time on creating it.  
So any donations are welcome but of course not required. 	(˵ ͡° ͜ʖ ͡°˵)  

[![Sponsor Link](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/gamingismyfood)

## Contributing
Contributions are always welcome!

## License

    Copyright 2021 Cecilio Silva Monteiro

    Licensed under the GNU General Public License v3.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    https://www.gnu.org/licenses/gpl-3.0-standalone.html

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

# Made by 🧑🏾‍💻

[@CecilioSilva](https://github.com/CecilioSilva)