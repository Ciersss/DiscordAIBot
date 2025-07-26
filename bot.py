import discord
import os
import requests
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

HEADERS = {
    "Authorization": f"{OPENAI_API_KEY}",
    "Content-Type": "application",
    "HTTP-Referer": "https://maftei.it",
    "X-Title": "Discord AI Bot"
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
conversations = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Connected')

@bot.tree.command(name="ask", description="Ask me something")
@app_commands.describe(prompt="Ask me something")
async def sommo(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()

    channel_id = interaction.channel.id
    history = conversations.get(channel_id, [])
    history.append({"role": "user", "content": prompt})

    try:
        body = {
            "model": "openai/gpt-3.5-turbo",
            "messages": history
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=HEADERS,
            json=body
        )

        data = response.json()

        if "choices" in data and data["choices"]:
            reply = data["choices"][0]["message"]["content"]
            history.append({"role": "assistant", "content": reply})
            conversations[channel_id] = history[-20:]
        else:
            print("Invalid response:", data)
            reply = "Unexpected response."

        MAX_LEN = 1900
        if len(reply) > MAX_LEN:
            for i in range(0, len(reply), MAX_LEN):
                await interaction.followup.send(reply[i:i+MAX_LEN])
        else:
            await interaction.followup.send(reply)

    except Exception as e:
        print("Error:", e)
        await interaction.followup.send("Errore.")

@bot.tree.command(name="reset", description="Reset conversation")
async def reset(interaction: discord.Interaction):
    conversations.pop(interaction.channel.id, None)
    await interaction.response.send_message("Conversation resetted.")

bot.run(DISCORD_TOKEN)
