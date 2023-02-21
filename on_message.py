import json
import re
import subprocess
import cv2
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import discord
from discord.ext.commands import Bot, Cog

import reference


class OnMessage(Cog):
    def __init__(self, client: Bot):
        self.client = client

    # Listener
    @Cog.listener()
    async def on_message(self, message):
        # Exec OS Level Commands with Sudo
        if message.content[0:4] == "sudo" and message.author.bot == False:
            if message.author.id == self.client.admin_id:
                try:
                    pipe = subprocess.Popen(
                        message.content,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    out, err = pipe.communicate()
                    error = err.decode()
                    response = out.decode()
                    combined = response + error
                    if combined == "":
                        await message.reply(
                            f"{self.client.checkmarkGlyph(message.guild)} Command executed with no output."
                        )
                    else:
                        await message.reply(f"```{combined}```")
                except discord.errors.HTTPException as _e:
                    await message.reply(self.client.xmarkGlyph(message.guild), _e)
            else:
                await message.reply(
                    f"You do not have permission to use this command. {self.client.xmarkGlyph(message.guild)}"
                )

        # Facial Recognition and Auto-Filtering
        links = set(
            re.findall(r"((?:http|https):(?:\w|\/|\.)+\.(?:jpg|png))", message.content)
        )

        for attachment in message.attachments:
            if attachment.content_type in ["image/png", "image/jpeg"]:
                links.add(attachment.url)

        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36"
        }
        for link in links:
            res = requests.get(link, headers=headers).content
            bytes = Image.open(BytesIO(bytearray(res)))
            img = np.array(bytes)

            cv2.imshow("Image", img)
            cv2.waitKey(5000)
            cv2.destroyAllWindows()

        # Chat Filter
        filtered_seqs = ["did you mean", "you meant", "you appear to have misspelt"]

        # for seq in filtered_seqs:
        #     if seq in message.content.lower():
        #         await message.delete()


# Setup & Link
async def setup(client: Bot):
    await client.add_cog(OnMessage(client))
