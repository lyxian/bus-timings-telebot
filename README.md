# bus-timings-telebot

Features:

- get current location geocode
- compile bus stops info
- get nearest bus stops in proximity
- get bus timings

Commands:

- /start - start replyMarkup

# Development

**preprod**

- get current location geocode (ok)
- compile bus stops info (ok)
- get nearest bus stops in proximity (ok)
- get bus timings (ok)

**v0**

- run on Telegram (ok)
- improve message
- reverse sorting order

**v1**

- show map
  - API
    - OneMap
    - StreetDirectory?
  - tasks :
    - nearest bus stops given location
    - plot on map
    - sendPhoto on Telegram
- custom configurations
  - radius
- mrt/lrt integration
- message tracking (pinned messages / database)
  - disappearing message

**extra**

- integrate encryptionStore

**fix**

- methodA is 4x slower than methodB
- sort bus error if non-numeric (ok)
- handle no bus data
- OneMap not loading remote areas (use layers=default)

# Reference

- OneMap
  - https://www.onemap.gov.sg/docs/#static-map
  - https://tools.onemap.gov.sg/staticmap/

##Packages (list required packages & run .scripts/python-pip.sh)
PyTelegramBotAPI
cryptography
pendulum
pyyaml
flask
numpy
bs4
##Packages
