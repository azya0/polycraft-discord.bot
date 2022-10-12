from configparser import ConfigParser
from os.path import exists
import builtins

import discord
from discord.ext import tasks
from requests import get


class PolyCraftBot(discord.Client):
    def __int__(self, *args, **kwargs):
        self.config = None
        super().__init__(*args, **kwargs)

    def connect_config(self, __config: ConfigParser):
        self.config = __config

    async def on_ready(self):
        print(f'{self.user} is ready')
        if self.config is None:
            raise ConnectionError('miss config')
        loops = [self.minecraft_server_online_stat, self.server_user_stat]
        for loop in loops:
            loop.change_interval(minutes=float(self.config['loop_time'][loop.__dict__['coro'].__name__]))
            loop.start()

    @tasks.loop()
    async def minecraft_server_online_stat(self):
        channel = self.get_channel(int(self.config[f'minecraft_server_online_stat']['channel_id']))
        if channel is None:
            print(f'[minecraft_server_online_stat] channel error')
            return
        try:
            data = str(get(f"https://api.mcsrvstat.us/2/{self.config['server']['ip']}").json()["players"]["online"])
        except KeyError:
            data = 'error'

        text = f'{self.config[f"minecraft_server_online_stat"]["channel_text"]}'.replace(
                self.config["settings"]["number_of_user_string"], data)

        if channel.name != text:
            print(f'changing minecraft_server_online_stat from {channel.name} to {text}')
            await channel.edit(name=text)

    @tasks.loop()
    async def server_user_stat(self):
        channel = self.get_channel(int(self.config[f'server_user_stat']['channel_id']))
        if channel is None:
            print(f'[server_user_stat] channel error')
            return

        text = f'{self.config["server_user_stat"]["channel_text"]}'.replace(
            self.config["settings"]["number_of_user_string"], str(len(self.users)))

        try:
            if channel.name != text:
                print(f'changing server_user_stat from {channel.name} to {text}')
                await channel.edit(name=text)
        except Exception as error:
            print(error)


if __name__ == '__main__':
    CONFIG_PATH = 'config.ini'
    config = ConfigParser()
    if exists(CONFIG_PATH):
        config.read(CONFIG_PATH, encoding='utf-8')
    else:
        raise FileExistsError(f'File {CONFIG_PATH} don\'t exist')

    print = lambda *args, **kwargs: (builtins.print("[Discord.Bot]", end=' '), builtins.print(*args, **kwargs))

    intents = discord.Intents.all()
    client = PolyCraftBot(intents=intents)
    client.connect_config(config)
    client.run(config['oauth2']['token'])
