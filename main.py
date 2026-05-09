import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL
from aiogram.types import FSInputFile

TOKEN = os.getenv('TOKEN_BOT')
bot = Bot(token=TOKEN)
dp = Dispatcher()

if not os.path.exists("downloads"):
    os.makedirs("downloads")

def download_media_sync(url, mode="video"):
    """Sinxron yuklab olish funksiyasi"""
    options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if mode == "video" else 'bestaudio/best',
        'outtmpl': f'downloads/%(title)s_{mode}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
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
    await message.answer("Salom! Link yuboring, men sizga video va audio qilib beraman.")

@dp.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    url = message.text
    status_msg = await message.answer("⏳ Ishlov berilmoqda...")
    
    loop = asyncio.get_event_loop()
    try:
        # Videoni asinxron chaqirish
        video_path = await loop.run_in_executor(None, download_media_sync, url, "video")
        await message.answer_video(FSInputFile(video_path), caption="🎬 Video tayyor!")
        
        # Audioni asinxron chaqirish
        audio_path = await loop.run_in_executor(None, download_media_sync, url, "audio")
        await message.answer_audio(FSInputFile(audio_path), caption="🎵 Audio tayyor!")
        
        # O'chirish
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        await status_msg.delete()
        
    except Exception as e:
        await message.answer(f"Xatolik: {str(e)}")
        if status_msg: await status_msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
