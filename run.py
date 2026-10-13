"""Inicia el laboratorio local leyendo .env sin dependencias extra."""

import os
import re
from pathlib import Path

import uvicorn


def load_env(path: Path) -> None:
    if not path.is_file():
        raise SystemExit("Falta .env. Copiá .env.example a .env y completá las claves.")
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.lstrip().startswith("#") or "=" not in raw:
            continue
        name, value = raw.split("=", 1)
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[name] = value


if __name__ == "__main__":
    load_env(Path(__file__).with_name(".env"))
    if not os.getenv("JARVIS_API_KEY"):
        raise SystemExit("Completá JARVIS_API_KEY en .env antes de iniciar.")
    print("Jarvis disponible en http://127.0.0.1:8010/demo")
    uvicorn.run("jarvis_noc.main:app", host="127.0.0.1", port=8010)
