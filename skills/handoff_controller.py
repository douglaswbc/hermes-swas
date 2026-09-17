import json
import time
from pathlib import Path

BASE = Path("/opt/data/hermes_bot_data/conversations")


def handle_command(cmd, args, conversation_id):
    file = BASE / f"{conversation_id}.json"
    if not file.exists():
        return "Conversa nao encontrada"
    data = json.loads(file.read_text())
    if cmd == "/assumir":
        mode = "timer"
        if "manual" in args:
            mode = "manual"
        if "inteligente" in args or "smart" in args:
            mode = "smart"
        hours = 2
        for arg in args:
            if "h" in arg:
                try:
                    hours = int(arg.replace("h", ""))
                except ValueError:
                    pass
        data["paused"] = True
        data["mode"] = mode
        data["paused_at"] = int(time.time())
        data["resume_at"] = int(time.time()) + hours * 3600 if mode == "timer" else None
        file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return f"✅ Pausado MODO {mode.upper()} para {conversation_id} - volta em {hours}h"
    if cmd == "/liberar":
        data["paused"] = False
        data["resume_at"] = None
        file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return f"✅ Liberado! Bot voltou para {conversation_id}"
    return "Comando desconhecido"


def check_resume():
    now = int(time.time())
    for file in BASE.glob("*.json"):
        try:
            data = json.loads(file.read_text())
            if data.get("paused") and data.get("resume_at") and now > data["resume_at"]:
                data["paused"] = False
                file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        except (OSError, json.JSONDecodeError):
            pass


if __name__ == "__main__":
    check_resume()
