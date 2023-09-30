import requests
import os
import time
import argparse
from io import StringIO
import csv

REFRESH_TIME = int(os.getenv("REFRESH_TIME"))

MDRC_TOML = "matterbridge_mdrc.toml"

MDRC_SHEET_ID = os.getenv("MDRC_SHEET_ID")
MDRC_DISCORD_TOKEN = os.getenv("MDRC_DISCORD_TOKEN")
MDRC_SLACK_TOKEN = os.getenv("MDRC_SLACK_TOKEN")
MDRC_DISCORD_SERVER = os.getenv("MDRC_DISCORD_SERVER")


def main():
    # set up argparse to look for if --continuous is present
    parser = argparse.ArgumentParser()
    parser.add_argument("--continuous", help="run continuously", action="store_true")
    args = parser.parse_args()

    run()

    if args.continuous:
        while True:
            time.sleep(REFRESH_TIME)
            #run()


def run():
    print("Creating MDRC TOML...")
    with open(MDRC_TOML, "w") as f:
        f.write(make_toml(MDRC_SHEET_ID, MDRC_DISCORD_TOKEN, MDRC_SLACK_TOKEN, MDRC_DISCORD_SERVER))


def make_toml(sheet_id, discord_token, slack_token, discord_server):
    channels = get_google_sheets_csv(sheet_id)

    s = ""
    s += get_base_toml(discord_token, slack_token, discord_server)

    for line in channels:
        s += make_channel_toml(*line)

    return s


def get_google_sheets_csv(sheet_id):
    response = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={sheet_id}&output=csv')
    f = StringIO(response.text)
    reader = csv.reader(f)
    next(reader)
    return reader


def get_base_toml(discord_token, slack_token, discord_server): return """
# --------------------------------------------------------------------------

[discord]
[discord.Discord]

Token=\"""" + discord_token + """\"

Server=\"""" + discord_server + """\"
AutoWebhooks=true

RemoteNickFormat="{NICK} [{PROTOCOL}] "
PreserveThreading=true
MediaDownloadSize=25000000

[slack]
[slack.Slack]
Token=\"""" + slack_token + """\"
RemoteNickFormat="{NICK} [{PROTOCOL}] "
PreserveThreading=true
MediaDownloadSize=25000000"""


def make_channel_toml(name, discord_id, slack_id): return """

[[gateway]]
name=\"""" + name + """\"
enable=true
[[gateway.inout]]
account="discord.Discord"
channel=\"""" + discord_id + """\"
[[gateway.inout]]
account="slack.Slack"
channel=\"""" + slack_id + """\"

"""


if __name__ == "__main__":
    main()
