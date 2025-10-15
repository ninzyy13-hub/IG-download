from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os
import instaloader
import tempfile

TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@REMEMBER_YOU 007"

LANGUAGES = {"km":"ខ្មែរ 🇰🇭","en":"English 🇺🇸","zh":"中文 🇨🇳","es":"Español 🇪🇸"}
MESSAGES = {
    "km": {"welcome":"ស្វាគមន៍🎉","subscribe":f"សូមជាវឆាណែល {CHANNEL_USERNAME}","drop_link":"ទម្លាក់តំណ Instagram","waiting":"សូមរង់ចាំ… ⏳"},
    "en": {"welcome":"Welcome 🎉","subscribe":f"Please subscribe {CHANNEL_USERNAME}","drop_link":"Drop Instagram link","waiting":"Please wait… ⏳"},
    "zh": {"welcome":"欢迎 🎉","subscribe":f"请先关注 {CHANNEL_USERNAME}","drop_link":"发送 Instagram 链接","waiting":"请稍候… ⏳"},
    "es": {"welcome":"Bienvenido 🎉","subscribe":f"Por favor suscríbete {CHANNEL_USERNAME}","drop_link":"Envía enlace Instagram","waiting":"Por favor espera… ⏳"}
}

user_lang = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v, callback_data=k)] for k,v in LANGUAGES.items()]
    await update.message.reply_text("🌍 Select language:", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data
    user_lang[query.from_user.id] = lang
    await query.answer()
    msg = MESSAGES[lang]
    await query.edit_message_text(f"{msg['welcome']}\n{msg['subscribe']}")

def download_instagram_media(url):
    L = instaloader.Instaloader(dirname_pattern=tempfile.gettempdir(), download_videos=True, save_metadata=False)
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    files = []
    if post.is_video:
        files.append(post.video_url)
    elif post.typename=="GraphSidecar":
        for node in post.get_sidecar_nodes():
            if node.is_video: files.append(node.video_url)
            else: files.append(node.display_url)
    else:
        files.append(post.url)
    return files

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = user_lang.get(user_id, "en")
    text = update.message.text
    if "instagram.com" in text:
        await update.message.reply_text(MESSAGES[lang]["waiting"])
        try:
            media_urls = download_instagram_media(text)
            for media_url in media_urls:
                if media_url.endswith(".mp4"):
                    await update.message.reply_video(media_url)
                else:
                    await update.message.reply_photo(media_url)
        except Exception as e:
            await update.message.reply_text(f"❌ Cannot download media. Error: {str(e)}")
    else:
        await update.message.reply_text(MESSAGES[lang]["drop_link"])

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(set_language))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.run_polling()
