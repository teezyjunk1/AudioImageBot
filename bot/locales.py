from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class L10n:
    start_choose_lang: str
    start_ready: str
    help_text: str
    send_audio_first: str
    send_image_first: str
    audio_ok_now_image: str
    image_ok_now_audio: str
    invalid_audio: str
    invalid_image: str
    building_video: str
    done: str
    error_generic: str
    change_lang_hint: str
    choose_lang_prompt: str
    tutorial_after_lang: str

RU = L10n(
    start_choose_lang=(
        "Привет! Выберите язык интерфейса — RU или EN. Вы всегда можете сменить язык командой /lang"
    ),
    choose_lang_prompt="Выберите язык:",
    start_ready=(
        "Готов к работе! Отправьте *MP3* аудио и фото (PNG/JPG), в любом порядке. Я соберу MP4 с фото на чёрном фоне."
    ),
    help_text=(
        "Отправьте аудио *в формате MP3* и фото (PNG/JPG) — можно как фото, так и файл.\n"
        "Я сделаю видео MP4 1920×1080: картинка по центру, вокруг чёрный фон.\n\n"
        "Команды:\n"
        "• /start — запуск\n"
        "• /lang — сменить язык"
    ),
    send_audio_first="Отправьте, пожалуйста, аудио в формате *MP3*.",
    send_image_first="Теперь пришлите изображение (PNG/JPG).",
    audio_ok_now_image="Аудио получено ✅ Теперь отправьте изображение (PNG/JPG).",
    image_ok_now_audio="Изображение получено ✅ Теперь отправьте аудио в формате *MP3*.",
    invalid_audio="Можно только MP3. Пришлите другой файл.",
    invalid_image="Нужен PNG или JPG. Пришлите другое изображение.",
    building_video="Собираю видео, подождите немного…",
    done="Готово! Вот ваше видео MP4.",
    error_generic="Упс, что-то пошло не так. Попробуйте ещё раз позже.",
    change_lang_hint="Вы можете сменить язык командой /lang",
    tutorial_after_lang=(
        "Язык обновлён. В будущем вы можете изменить язык командой /lang.\n\n"
        "Отправьте MP3 и PNG/JPG — соберу видео."
    ),
)

EN = L10n(
    start_choose_lang=(
        "Hi! Choose interface language — RU or EN. You can always change it later via /lang"
    ),
    choose_lang_prompt="Choose a language:",
    start_ready=(
        "Ready! Send *MP3* audio and a PNG/JPG photo, in any order. I will produce an MP4 with your image centered on black."
    ),
    help_text=(
        "Send audio *in MP3 format* and an image (PNG/JPG) — as photo or file.\n"
        "I will produce a 1920×1080 MP4: image centered with black background.\n\n"
        "Commands:\n"
        "• /start — start\n"
        "• /lang — change language"
    ),
    send_audio_first="Please send an *MP3* audio first.",
    send_image_first="Now send an image (PNG/JPG).",
    audio_ok_now_image="Audio received ✅ Now send an image (PNG/JPG).",
    image_ok_now_audio="Image received ✅ Now send an *MP3* audio.",
    invalid_audio="MP3 only, please. Send a different file.",
    invalid_image="PNG or JPG only, please.",
    building_video="Building your video, please wait…",
    done="Done! Here is your MP4.",
    error_generic="Oops, something went wrong. Please try again later.",
    change_lang_hint="You can change language with /lang",
    tutorial_after_lang=(
        "Language updated. In the future you can change it with /lang.\n\n"
        "Send MP3 and PNG/JPG — I will build the video."
    ),
)

LANGS: Dict[str, L10n] = {"RU": RU, "EN": EN}