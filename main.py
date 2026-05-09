import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Fayllarni vaqtincha saqlash uchun papka
if not os.path.exists("downloads"):
    os.makedirs("downloads")

def download_media(url, mode="video"):
    """Video yoki Audio yuklab olish funksiyasi"""
    options = {
        'format': 'best' if mode == "video" else 'bestaudio/best',
        'outtmpl': f'downloads/%(title)s_{mode}.%(ext)s',
    }
    
    if mode == "audio":
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == "audio":
            filename = filename.rsplit('.', 1)[0] + ".mp3"
        return filename

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Salom! Instagram yoki YouTube linkini yuboring, men sizga video va musiqasini yuklab beraman.")

@dp.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    url = message.text
    status_msg = await message.answer("⏳ Ishlov berilmoqda, kuting...")
    
    try:
        # Video yuklash
        video_file = download_media(url, mode="video")
        await message.answer_video(types.FSInputFile(video_file), caption="🎬 Video tayyor!")
        
        # Audio yuklash
        audio_file = download_media(url, mode="audio")
        await message.answer_audio(types.FSInputFile(audio_file), caption=" Musiqasi tayyor!")
        
        # Fayllarni o'chirish (joy egallamasligi uchun)
        os.remove(video_file)
        os.remove(audio_file)
        await status_msg.delete()
        
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")
        await status_msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
