import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

SETTINGS_FILE = Path("user_settings.json")
SESSIONS_FILE = Path("sessions.json")

@dataclass
class UserSettings:
    lang: str  # "RU" or "EN"

class Storage:
    def __init__(self):
        self._users: Dict[str, UserSettings] = {}
        self._sessions: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                self._users = {k: UserSettings(**v) for k, v in raw.items()}
        if SESSIONS_FILE.exists():
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                self._sessions = json.load(f)

    def _save_users(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({k: v.__dict__ for k, v in self._users.items()}, f, ensure_ascii=False, indent=2)

    def _save_sessions(self):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._sessions, f, ensure_ascii=False, indent=2)

    # User settings
    def get_lang(self, user_id: int) -> Optional[str]:
        u = self._users.get(str(user_id))
        return u.lang if u else None

    def set_lang(self, user_id: int, lang: str):
        self._users[str(user_id)] = UserSettings(lang=lang)
        self._save_users()

    # Session: holds paths to uploaded audio/image until we render
    def get_session(self, user_id: int) -> Dict:
        return self._sessions.get(str(user_id), {})

    def update_session(self, user_id: int, **kwargs):
        sid = str(user_id)
        sess = self._sessions.get(sid, {})
        sess.update(kwargs)
        self._sessions[sid] = sess
        self._save_sessions()

    def clear_session(self, user_id: int):
        self._sessions.pop(str(user_id), None)
        self._save_sessions()