# soybot

A Discord bot made by eesoymilk.

## Slash Commands

- Reaction Poll: `/poll`

- Waifu.im: `/waifu`

- Inspect a user's avatar: `/avatar`

- Emoji Kitchen: `/emoji_kitchen`

## Run the bot locally

1. Setup `.env`

   ```
   TOKEN=<your_bot_token_here>
   OPENAI_API_KEY=<your_openai_api_key_here>
   ```

1. Build and run

- Option 1: Docker
  This is the recommended way to start this bot. Make sure you have docker installed and run the following commands:

  ```shell
  docker compose pull
  docker compose --env-file <path/to/.env> up
  ```

- Option 2: Without docker (not recommended)
  We use `venv` to handle our environment. Note that depending on different OS, the commands may be different.
  ```shell
  python3 -m venv venv
  source venv/bin/activare
  python3 lancher.py
  ```
