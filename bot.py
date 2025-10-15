from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import asyncio
import os
import instaloader

TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@YourChannelHere"

LANGUAGES = {
    "km": "ភាសាខ្មែរ 🇰🇭",
    "en": "English 🇺🇸",
    "zh": "中文 🇨🇳",
    "es": "Español 🇪🇸"
}

MESSAGES = {
    "km": {
        "welcome": "សូមស្វាគមន៍មកកាន់ IG Video Downloader Bot 🎉",
        "subscribe": f"សូមជាវឆាណែល {CHANNEL_USERNAME} មុននឹងប្រើសេវា។",
        "drop_link": "អ្នកអាចទម្លាក់តំណវីដេអូ Instagram នៅទីនេះ។ ខ្ញុំនឹងជួយអ្នកដោនឡូត។",
        "waiting": "សូមរង់ចាំ… ⏳"
    },
    "en": {
        "welcome": "Welcome to IG Video Downloader Bot 🎉",
        "subscribe": f"Please subscribe to {CHANNEL_USERNAME} before using this bot.",
        "drop_link": "You can drop your Instagram video link here. I’ll help you download it.",
        "waiting": "Please wait… ⏳"
    },
    "zh": {
        "welcome": "欢迎使用 IG 视频下载机器人 🎉",
        "subscribe": f"请先关注频道 {CHANNEL_USERNAME}。",
        "drop_link": "请发送 Instagram 视频链接，我会帮你下载。",
        "waiting": "请稍候… ⏳"
    },
    "es": {
        "welcome": "Bienvenido al bot IG Video Downloader 🎉",
        "subscribe": f"Por favor, suscríbete a {CHANNEL_USERNAME} antes de usar este bot.",
        "drop_link": "Puedes enviar tu enlace de video de Instagram aquí. Te ayudaré a descargarlo.",
        "waiting": "Por favor espera… ⏳"
    }
}

user_lang = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v, callback_data=k)] for k, v in LANGUAGES.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 Please select your language:", reply_markup=reply_markup)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data
    user_lang[query.from_user.id] = lang
    await query.answer()
    msg = MESSAGES[lang]
    await query.edit_message_text(f"{msg['welcome']}\n\n{msg['subscribe']}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = user_lang.get(user_id, "en")
    text = update.message.text

    if "instagram.com" in text:
        await update.message.reply_text(MESSAGES[lang]["waiting"])

        # 🔹 Start downloading video using instaloader
        try:
            L = instaloader.Instaloader(dirname_pattern="downloads", download_videos=True, download_comments=False, download_geotags=False, save_metadata=False)
            post_url = text
            post = instaloader.Post.from_shortcode(L.context, post_url.split("/")[-2])
            video_url = post.video_url

            # 🔹 Send video as Telegram file
            await update.message.reply_video(video_url)

        except Exception as e:
            await update.message.reply_text(f"❌ Cannot download video. Error: {str(e)}")

    else:
        await update.message.reply_text(MESSAGES[lang]["drop_link"])

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(set_language))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
