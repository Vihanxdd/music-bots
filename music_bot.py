import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

# =====================
# APNA TOKEN YAHAN DAALO
BOT_TOKEN = "YAHAN_APNA_NAYA_TOKEN_DAALO"
# =====================

CHANNEL = "@SecretChor"

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Channel Join Check
def check_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ✅ Join Button
def join_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/SecretChor"))
    markup.add(InlineKeyboardButton("✅ Joined! Continue", callback_data="check_join"))
    return markup

# ✅ /start Command
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    if not check_joined(user_id):
        bot.send_message(
            message.chat.id,
            "🎵 *Music Bot mein Aapka Swagat Hai!*\n\n"
            "⚠️ Bot use karne ke liye pehle hamare channel ko join karo:",
            parse_mode="Markdown",
            reply_markup=join_button()
        )
    else:
        bot.send_message(
            message.chat.id,
            "🎵 *Music Bot mein Aapka Swagat Hai!*\n\n"
            "Koi bhi gaana ka naam likho — main dhundh dunga! 🎶",
            parse_mode="Markdown"
        )

# ✅ Join Check Callback
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_callback(call):
    user_id = call.from_user.id
    if check_joined(user_id):
        bot.answer_callback_query(call.id, "✅ Shukriya! Ab bot use kar sakte ho!")
        bot.send_message(
            call.message.chat.id,
            "🎵 *Bahut Acha!*\n\nAb koi bhi gaana ka naam likho! 🎶",
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Abhi tak join nahi kiya!", show_alert=True)

# ✅ Music Search
@bot.message_handler(func=lambda message: True)
def search_music(message):
    user_id = message.from_user.id

    if not check_joined(user_id):
        bot.send_message(
            message.chat.id,
            "⚠️ Pehle channel join karo!",
            reply_markup=join_button()
        )
        return

    query = message.text
    bot.send_message(message.chat.id, f"🔍 *'{query}'* dhundh raha hoon...", parse_mode="Markdown")

    # Search YouTube
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch5',
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)
            videos = results.get('entries', [])

        if not videos:
            bot.send_message(message.chat.id, "❌ Koi result nahi mila. Dobara try karo!")
            return

        # Show top 5 results
        markup = InlineKeyboardMarkup()
        for i, video in enumerate(videos[:5]):
            title = video.get('title', 'Unknown')[:40]
            video_id = video.get('id', '')
            markup.add(
                InlineKeyboardButton(
                    f"🎵 {title}",
                    callback_data=f"select_{video_id}"
                )
            )

        bot.send_message(
            message.chat.id,
            "🎶 *Results:*\n\nEk gaana select karo:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Kuch error hua. Dobara try karo!")

# ✅ Song Select — Video ya Audio choose karo
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def select_song(call):
    video_id = call.data.replace("select_", "")
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎵 Audio (MP3)", callback_data=f"audio_{video_id}"),
        InlineKeyboardButton("🎬 Video (MP4)", callback_data=f"video_{video_id}")
    )
    bot.edit_message_text(
        "📥 *Aap kya chahte ho?*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ✅ Audio Download
@bot.callback_query_handler(func=lambda call: call.data.startswith("audio_"))
def download_audio(call):
    video_id = call.data.replace("audio_", "")
    url = f"https://www.youtube.com/watch?v={video_id}"
    bot.answer_callback_query(call.id, "⏳ Audio download ho raha hai...")
    bot.send_message(call.message.chat.id, "⏳ *Audio download ho raha hai... thoda wait karo!*", parse_mode="Markdown")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{video_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        audio_file = f"{video_id}.mp3"
        with open(audio_file, 'rb') as f:
            bot.send_audio(call.message.chat.id, f)
        os.remove(audio_file)

    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ Audio download nahi hua. Dobara try karo!")

# ✅ Video Download
@bot.callback_query_handler(func=lambda call: call.data.startswith("video_"))
def download_video(call):
    video_id = call.data.replace("video_", "")
    url = f"https://www.youtube.com/watch?v={video_id}"
    bot.answer_callback_query(call.id, "⏳ Video download ho raha hai...")
    bot.send_message(call.message.chat.id, "⏳ *Video download ho raha hai... thoda wait karo!*", parse_mode="Markdown")

    ydl_opts = {
        'format': 'best[filesize<50M]',
        'outtmpl': f'{video_id}.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get('ext', 'mp4')

        video_file = f"{video_id}.{ext}"
        with open(video_file, 'rb') as f:
            bot.send_video(call.message.chat.id, f)
        os.remove(video_file)

    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ Video download nahi hua. Dobara try karo!")

# ✅ Bot Start
print("🎵 Music Bot Chalu Ho Gaya!")
bot.infinity_polling()
