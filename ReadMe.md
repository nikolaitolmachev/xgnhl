# xGNHL
xGNHL - console application which calculates a value between pinnacle's odds and odds which are produced by xG data from
naturalstattrick.com using Poisson distribution for NHL matches.

![Demo 1](https://github.com/nikolaitolmachev/xgnhl/raw/main/Img/scr_1.jpg)

## How to install ?
It is a python (3.6) application, so you need have installed it on your PK.

Clone the repository:
```
https://github.com/nikolaitolmachev/xgnhl.git
```

Upgrade pip:
```
python3 -m pip install --upgrade pip
```

Install libs:
```
pip install -r requirements.txt
```

## How to use ?

Follow the instructions.
You can choice to use the application via a proxy or no. There is because naturalstattrick.com can kick due to a large number of requests.
To analyze a single NHL match - put a URL of NHL match from betexplorer.com, for example, https://www.betexplorer.com/hockey/usa/nhl/washington-capitals-detroit-red-wings/A1U24YZd/.

![Demo 2](https://github.com/nikolaitolmachev/xgnhl/raw/main/Img/scr_2.jpg)

### settings.ini
MINIMAL_MATCHES_TO_COUNT - minimal played matches for a team to calculate. Meaning at home/away because it is different data of xG.  Default: 3.

MODEL_VALUE_DIFFERENCE - % of difference odds deviations (value) to save in stats.txt. Default: 30.

PROXY - proxy in the next format: type://login:password@IP:port.

USER_AGENT - user agent.

## GL!