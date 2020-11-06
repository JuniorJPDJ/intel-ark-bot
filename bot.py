import asyncio
import logging

import aiohttp
from telethon import TelegramClient, events
from telethon.tl.custom import InlineBuilder

import yaml

async def main(config):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config['log_level'])
    # logger = logging.getLogger(__name__)

    client = TelegramClient(**config['telethon_settings'])
    print("Starting")
    await client.start(bot_token=config['bot_token'])
    print("Started")

    async with aiohttp.ClientSession(raise_for_status=True) as http_sess:
        builder = InlineBuilder(client)

        @client.on(events.InlineQuery)
        async def inline_handler(event):
            if not event.text or len(event.text) < 2:
                await event.answer()
                return
            

            try:
                resp = await http_sess.get("https://ark.intel.com/libs/apps/intel/arksearch/autocomplete", params={
                    "_charset_": "UTF-8",
                    "locale": "en_us",
                    "currentPageUrl": "https://ark.intel.com/content/www/us/en/ark.html",
                    "input_query": event.text
                })
                results = await resp.json()
            except aiohttp.ClientResponseError:
                await event.answer([builder.article("Error occured while searching", description="Oops ;/", text="Oops ;/")])
                return

            await event.answer(
                [builder.article(title=r['label'], text="https://ark.intel.com"+r['prodUrl']) for r in results] or 
                [builder.article("No search results found", description="Try another query", text="No search results found.")]
            )

        async with client:
            print("Good morning!")
            await client.run_until_disconnected()


if __name__ == '__main__':
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)
    asyncio.get_event_loop().run_until_complete(main(config))

