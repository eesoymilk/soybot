# soybot
A discord bot written in `discord.py` by eesoymilk.

## Slash Commands

- Reaction Poll: `/poll`
 
- Waifu.im: `/waifu`

- Inspect a user's avatar: `/avatar`

- Emoji Kitchen: `/emoji_kitchen`

## Run the bot locally

1. Setup `.env`
  ```
  TOKEN=<your_bot_token_here>
  MONGODB_CONNECTION_STR=<your_mongodb_connection_string_here>
  OPENAI_API_KEY=<your_openai_api_key_here>
  ```

1. Build and run

  - Option 1: Docker
    This is the recommended way to start this bot. Make sure you have docker installed and run the following commands:
    ```shell
    docker build -t <image-name:tag> .
    docker run --env-file=.env --name <container-name> <image-name:tag>
    ```

  - Option 2: Without docker (not recommended)
    We use `venv` to handle our environment. Note that depending on different OS, the commands may be different.
    ```shell
    python3 -m venv venv
    source venv/bin/activare
    python3 lancher.py
    ```

## Deploy to ACI (Azure Container Instance)

I'll document this later if I ever have time to. For now, let me just provide some useful refereces:

- [Configure a GitHub Action to create a container instance](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-github-action?tabs=userlevel)

- [GitHub Action - Deploy to Azure Container Instances](https://github.com/marketplace/actions/deploy-to-azure-container-instances)
