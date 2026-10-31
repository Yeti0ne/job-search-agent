#!/usr/bin/env python3
"""Génère AGENTS.md (version portable, tout assistant IA) depuis le skill.

Source unique : skills/recherche-emploi/SKILL.md
Sortie        : AGENTS.md = portable/adapter-preamble.md + corps du skill (sans l'en-tête YAML)

Usage :
  python3 scripts/build_portable.py           écrit AGENTS.md
  python3 scripts/build_portable.py --check   échoue si AGENTS.md n'est pas à jour, si le prompt
                                              compact dépasse 8000 caractères (limite des
                                              instructions d'un GPT personnalisé) ou si ses poids
                                              de notation diffèrent de ceux du skill
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "recherche-emploi" / "SKILL.md"
PREAMBLE = ROOT / "portable" / "adapter-preamble.md"
COMPACT = ROOT / "portable" / "agent-prompt-compact.md"
OUT = ROOT / "AGENTS.md"
COMPACT_LIMIT = 8000


def build() -> str:
    skill = SKILL.read_text(encoding="utf-8")
    body = re.sub(r"\A---\n.*?\n---\n", "", skill, count=1, flags=re.S).lstrip("\n")
    return PREAMBLE.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + body.rstrip("\n") + "\n"


def weights(text: str):
    m = re.search(r"Total 100 = [^.\n]*", text)
    return m.group(0) if m else None


def check() -> int:
    errors = []
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != build():
        errors.append("AGENTS.md n'est pas à jour : lancer python3 scripts/build_portable.py")
    compact = COMPACT.read_text(encoding="utf-8")
    if len(compact) > COMPACT_LIMIT:
        errors.append(f"portable/agent-prompt-compact.md fait {len(compact)} caractères (limite {COMPACT_LIMIT})")
    w_skill = weights(SKILL.read_text(encoding="utf-8"))
    if not w_skill:
        errors.append("la ligne « Total 100 = … » est introuvable dans le skill")
    elif w_skill not in compact:
        errors.append("le prompt compact n'a pas les mêmes poids de notation que le skill : « " + w_skill + " »")
    for e in errors:
        print("ERREUR :", e)
    if not errors:
        print(f"OK : AGENTS.md à jour, prompt compact {len(compact)}/{COMPACT_LIMIT} caractères, poids identiques")
    return 1 if errors else 0


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        sys.exit(check())
    OUT.write_text(build(), encoding="utf-8")
    print(f"écrit {OUT.relative_to(ROOT)} ({OUT.stat().st_size} octets)")
