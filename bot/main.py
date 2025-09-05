import asyncio
import os
from pathlib import Path
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from storage import Storage
from locales import LANGS
from ffmpeg_utils import build_video, WORKDIR

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_OUTPUT_MB = int(os.getenv("MAX_OUTPUT_MB", "45"))

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN is not set")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
storage = Storage()

# Helpers

def t(user_id: int, key: str) -> str:
    lang = storage.get_lang(user_id) or "RU"
    return getattr(LANGS[lang], key)

async def prompt_lang(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="RU", callback_data="lang:RU")
    kb.button(text="EN", callback_data="lang:EN")
    await message.answer(t(message.from_user.id, "choose_lang_prompt"), reply_markup=kb.as_markup())

# Commands

@dp.message(Command("start"))
async def cmd_start(message: Message):
    uid = message.from_user.id
    lang = storage.get_lang(uid)
    if lang is None:
        # first run → ask language
        await message.answer(LANGS["RU"].start_choose_lang + "\n\n" + LANGS["EN"].start_choose_lang)
        await prompt_lang(message)
    else:
        # already configured → go straight to instructions
        await message.answer(t(uid, "start_ready"))
        await message.answer(t(uid, "help_text"))

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(t(message.from_user.id, "help_text"))

@dp.message(Command("lang"))
async def cmd_lang(message: Message):
    await prompt_lang(message)

@dp.callback_query(F.data.startswith("lang:"))
async def on_lang_choice(cb: CallbackQuery):
    uid = cb.from_user.id
    lang = cb.data.split(":", 1)[1]
    if lang not in LANGS:
        await cb.answer("Unknown language", show_alert=True)
        return
    storage.set_lang(uid, lang)
    await cb.answer("OK")
    await cb.message.answer(LANGS[lang].tutorial_after_lang)
    await cb.message.answer(LANGS[lang].start_ready)
    await cb.message.answer(LANGS[lang].help_text)

# Content detection

def is_mp3(msg: Message) -> bool:
    doc = msg.document
    aud = msg.audio
    if aud and (aud.mime_type == "audio/mpeg" or (aud.file_name or "").lower().endswith(".mp3")):
        return True
    if doc and ((doc.mime_type == "audio/mpeg") or (doc.file_name or "").lower().endswith(".mp3")):
        return True
    return False

async def download_file(message: Message, file_id: str, suffix: str) -> Path:
    file = await bot.get_file(file_id)
    dest = WORKDIR / f"{message.from_user.id}_{file.file_unique_id}.{suffix}"
    await bot.download_file(file.file_path, destination=dest)
    return dest

async def handle_audio(message: Message):
    uid = message.from_user.id
    if not is_mp3(message):
        await message.reply(t(uid, "invalid_audio"))
        return
    file_id: Optional[str] = None
    if message.audio:
        file_id = message.audio.file_id
    elif message.document:
        file_id = message.document.file_id
    if not file_id:
        await message.reply(t(uid, "invalid_audio"))
        return
    apath = await download_file(message, file_id, "mp3")
    storage.update_session(uid, audio=str(apath))
    sess = storage.get_session(uid)
    if sess.get("image"):
        await build_and_send(uid, message)
    else:
        await message.reply(t(uid, "audio_ok_now_image"))

async def handle_image(message: Message):
    uid = message.from_user.id
    file_id: Optional[str] = None
    suffix: Optional[str] = None
    if message.photo:
        # choose the largest size
        photo = message.photo[-1]
        file_id = photo.file_id
        suffix = "jpg"
    elif message.document:
        name = (message.document.file_name or "").lower()
        mt = (message.document.mime_type or "").lower()
        if name.endswith((".png", ".jpg", ".jpeg")) or mt in {"image/png", "image/jpeg"}:
            file_id = message.document.file_id
            suffix = "png" if name.endswith(".png") or mt == "image/png" else "jpg"
    if not file_id:
        await message.reply(t(uid, "invalid_image"))
        return
    ipath = await download_file(message, file_id, suffix)
    storage.update_session(uid, image=str(ipath))
    sess = storage.get_session(uid)
    if sess.get("audio"):
        await build_and_send(uid, message)
    else:
        await message.reply(t(uid, "image_ok_now_audio"))

async def build_and_send(uid: int, message: Message):
    l10n = LANGS[storage.get_lang(uid) or "RU"]
    sess = storage.get_session(uid)
    image_path = Path(sess.get("image"))
    audio_path = Path(sess.get("audio"))
    if not image_path.exists() or not audio_path.exists():
        await message.reply(l10n.error_generic)
        storage.clear_session(uid)
        return
    await message.reply(l10n.building_video)
    try:
        out = await build_video(image_path, audio_path)
        size_mb = out.stat().st_size / (1024 * 1024)
        if size_mb > MAX_OUTPUT_MB:
            await message.reply(
                ("⚠️ Output is large: ~" + f"{size_mb:.1f} MB" + ". Trying to send anyway…")
                if storage.get_lang(uid) == "EN"
                else ("⚠️ Большой файл: ~" + f"{size_mb:.1f} MB" + ". Пробую отправить…")
            )
        await message.reply_video(video=FSInputFile(out), caption=l10n.done)
    except Exception:
        await message.reply(l10n.error_generic)
    finally:
        storage.clear_session(uid)
        for p in (image_path, audio_path):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

# Routing

@dp.message(F.audio)
async def _on_audio(message: Message):
    await handle_audio(message)

@dp.message(F.photo)
async def _on_photo(message: Message):
    await handle_image(message)

@dp.message(F.document)
async def _on_document(message: Message):
    # Route documents to the correct handler
    if is_mp3(message):
        await handle_audio(message)
    else:
        await handle_image(message)

# Fallback text
@dp.message()
async def on_text(message: Message):
    uid = message.from_user.id
    lang = storage.get_lang(uid)
    if lang is None:
        await message.reply(LANGS["RU"].start_choose_lang + "\n\n" + LANGS["EN"].start_choose_lang)
        await prompt_lang(message)
    else:
        await message.reply(t(uid, "help_text") + "\n\n" + t(uid, "change_lang_hint"))

async def main():
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass