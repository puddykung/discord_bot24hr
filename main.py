import discord
from discord.ext import commands
from discord import app_commands, Interaction, ButtonStyle
from discord.ui import View, Button, Modal, TextInput
from datetime import datetime
import requests
import re
import os
import pytz  # ใช้สำหรับกำหนดโซนเวลา

WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1355631108825547053/IcN1liw0m36ly7OjNTdVeMomhTshH1GJ5r2iBdMNQIt8zzBnzDSO45xDF0oGqmJ10xi1"
GUILD_ID = 1355631041339064320  # เปลี่ยนเป็น ID ของเซิร์ฟเวอร์

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# ฟังก์ชันดึงเวลาปัจจุบัน (ใช้โซนเวลาไทย)
def get_current_time():
    tz = pytz.timezone("Asia/Bangkok")  # กำหนดโซนเวลาเป็นไทย
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

class ReviewModal(Modal, title="📝 เบิกของจาก"):
    review = TextInput(
        label="กรุณาพิมพ์ของที่เบิก พร้อม จำนวน",
        placeholder="ตัวอย่าง\nเกราะ 10\nAED 30\nเงินแดง 5000",
        style=discord.TextStyle.paragraph
    )
    reason = TextInput(
        label="เบิกไปทำอะไร?",
        placeholder="เช่น ขึ้นอาวุธ หรือ คราฟบราๆ",
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: Interaction):
        review_text = self.review.value.strip()
        reason_text = self.reason.value.strip()
        current_time = get_current_time()

        # ใช้ regex จับคู่ "ชื่อไอเทม" + "จำนวน" (ตัวเลข)
        matches = re.findall(r"(.+?)\s+(\d+)", review_text)
        
        items = []
        for name, quantity in matches:
            name = name.strip()
            if name in ["เงินแดง", "เงินเขียว", "เงิน"]:
                items.append(f"+ {name} : {quantity} $")  # ใส่ $ ไว้ข้างหลัง
            else:
                items.append(f"+ {name} : {quantity} ชิ้น")

        # จัดรูปแบบข้อความให้เป็น Code Block + แถบสี
        formatted_text = (
            f"```yaml\n"
            f"📝 เบิกของจาก : {interaction.user.display_name}\n\n"
            + "\n".join(items) +
            f"\n\n🔹 เวลาที่เบิก: {current_time}\n"
            f"📌 คราฟ: {reason_text}\n"
            f"```\n"
            f"=================================="
        )

        # ส่งข้อมูลไปยัง Webhook
        requests.post(WEBHOOK_URL, json={"content": formatted_text})

        await interaction.response.send_message("✅ เบิกของสำเร็จ!", ephemeral=True)

class ReviewView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="เบิกของ", style=ButtonStyle.green)
    async def review_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(ReviewModal())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Sync failed: {e}")

@bot.tree.command(name="เบิกของ", description="ส่งปุ่มให้ลูกค้ากดเพื่อเบิกของ")
async def review(interaction: Interaction):
    gif_url = "https://img2.imgbiz.com/imgbiz/bro-pumpfun.gif"
    
    embed = discord.Embed(title="📦 กดปุ่มด้านล่างเพื่อเบิกของนะครับ!", color=discord.Color.blue())
    embed.set_image(url=gif_url)
    
    await interaction.response.send_message(embed=embed, view=ReviewView())

bot.run(os.getenv('TOKEN'))
