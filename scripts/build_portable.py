#!/usr/bin/env python3
"""Génère AGENTS.md (version portable, tout assistant IA) depuis le skill.

Source unique : skills/recherche-emploi/SKILL.md
Sortie        : AGENTS.md = portable/adapter-preamble.md + corps du skill (sans l'en-tête YAML)

Usage :
  python3 scripts/build_portable.py           écrit AGENTS.md
  python3 scripts/build_portable.py --check   échoue si AGENTS.md n'est pas à jour, si le prompt
                                              compact dépasse 8000 caractères (limite des
                                              instructions d'un GPT personnalisé) ou si ses poids
                                              de notation diffèrent de ceux du skill, ou si les champs,
                                              statuts et champs de profil du skill ne se retrouvent pas
                                              dans le prompt compact, DATA.md et PROFILE.md
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "recherche-emploi" / "SKILL.md"
PREAMBLE = ROOT / "portable" / "adapter-preamble.md"
COMPACT = ROOT / "portable" / "agent-prompt-compact.md"
DATA = ROOT / "portable" / "DATA.md"
PROFILE = ROOT / "portable" / "PROFILE.md"
OUT = ROOT / "AGENTS.md"
COMPACT_LIMIT = 8000


def build() -> str:
    skill = SKILL.read_text(encoding="utf-8")
    body = re.sub(r"\A---\n.*?\n---\n", "", skill, count=1, flags=re.S).lstrip("\n")
    return PREAMBLE.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + body.rstrip("\n") + "\n"


def weights(text: str):
    m = re.search(r"Total 100 = [^.\n]*", text)
    return m.group(0) if m else None


def skill_fields(text: str):
    """Champs « Après candidature » de la collection offers, lus dans le skill."""
    m = re.search(r"Après candidature : (.*?)\. Textes générés", text, flags=re.S)
    if not m:
        return []
    seg = re.sub(r"\([^)]*\)", "", m.group(1))
    names = []
    for piece in re.split(r",| et ", seg):
        w = piece.strip().split(" ")[0] if piece.strip() else ""
        if re.fullmatch(r"[a-z]+(?:_[a-z]+)*", w):
            names.append(w)
    return names


def skill_fields_veille(text: str):
    """Champs « Veille et vérification » (hors prompt compact : voir DATA.md)."""
    m = re.search(r"Veille et vérification : (.*?)\. Après candidature", text, flags=re.S)
    if not m:
        return []
    seg = re.sub(r"\([^)]*\)", "", m.group(1))
    seg = re.sub(r"et si l'annonce les donne", "", seg)
    return [w.strip() for w in re.split(r",| et ", seg) if re.fullmatch(r"[a-z]+(?:_[a-z]+)*", w.strip())]


def skill_statuses(text: str):
    m = re.search(r"^- Statuts : (.*)\.$", text, flags=re.M)
    return [x.strip() for x in m.group(1).split(",")] if m else []


def profile_fields(text: str):
    m = re.search(r"le document `config/profile` \(champs : (.*?)\)\.\n", text, flags=re.S)
    if not m:
        return []
    seg = re.sub(r"\{[^}]*\}", "", m.group(1))
    seg = re.sub(r"\([^)]*\)", "", seg)
    return [w.strip() for w in seg.split(",") if re.fullmatch(r"[a-z_]+", w.strip())]


def cv_fields(text: str):
    m = re.search(r"le document `config/cv` \(champs : (.*?)\)", text, flags=re.S)
    return [w.strip() for w in m.group(1).split(",") if re.fullmatch(r"[a-z_]+", w.strip())] if m else []


def check_page(skill_text, statuses, data, profile, errors):
    page_file = ROOT / "skills" / "recherche-emploi" / "assets" / "radar-page.html"
    if not page_file.exists():
        errors.append("la page du Radar skills/recherche-emploi/assets/radar-page.html est introuvable")
        return
    page = page_file.read_text(encoding="utf-8")
    if len(page.encode("utf-8")) > 16_000_000:
        errors.append("la page du Radar dépasse 16 Mo")
    if "assets/radar-page.html" not in skill_text:
        errors.append("le skill ne cite pas assets/radar-page.html")
    for st in statuses:
        if f'["{st}",' not in page:
            errors.append(f"le statut {st} du skill manque dans la page du Radar")
    for doc in ("match_grid", "profile", "cv"):
        if f'x.id === "{doc}"' not in page:
            errors.append(f"la page du Radar ne lit pas config/{doc}")
    cvf = cv_fields(skill_text)
    if len(cvf) < 6:
        errors.append(f"champs de config/cv mal lus dans le skill ({len(cvf)})")
    for f in cvf:
        if f"d.{f}" not in page:
            errors.append(f"le champ {f} de config/cv n'est pas lu par la page du Radar")
        if f"`{f}`" not in profile and f'"{f}"' not in profile:
            errors.append(f"le champ {f} de config/cv manque dans portable/PROFILE.md")
        if f not in data:
            errors.append(f"le champ {f} de config/cv manque dans portable/DATA.md")
    for f in profile_fields(skill_text):
        if f"d.{f}" not in page and f'"{f}"' not in page and f in ("country", "timezone", "work_week", "currency", "local_language", "home_area", "job_sites", "weekly_target", "target_roles"):
            errors.append(f"le champ {f} de config/profile n'est pas lu par la page du Radar")
    for hard in ("Asia/Jerusalem",):
        if hard in page:
            errors.append(f"fuseau écrit en dur dans la page : {hard}")
    import shutil, subprocess, tempfile
    node = shutil.which("node")
    if node:
        i = page.find("<script>\n(function")
        j = page.find("</script>", i)
        if i >= 0 and j > i:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
                fh.write(page[i + 8:j])
            r = subprocess.run([node, "--check", fh.name], capture_output=True, text=True)
            if r.returncode != 0:
                errors.append("le script de la page du Radar a une erreur de syntaxe : " + r.stderr.strip().splitlines()[0][:120])


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
    skill_text = SKILL.read_text(encoding="utf-8")
    data = DATA.read_text(encoding="utf-8") if DATA.exists() else ""
    profile = PROFILE.read_text(encoding="utf-8") if PROFILE.exists() else ""
    if not DATA.exists():
        errors.append("portable/DATA.md est introuvable")
    if not PROFILE.exists():
        errors.append("portable/PROFILE.md est introuvable")
    fields = skill_fields(skill_text)
    if len(fields) < 10:
        errors.append(f"champs « Après candidature » mal lus dans le skill ({len(fields)})")
    for f in fields:
        if f not in compact:
            errors.append(f"le champ {f} du skill manque dans le prompt compact")
        if f not in data:
            errors.append(f"le champ {f} du skill manque dans portable/DATA.md")
    vf = skill_fields_veille(skill_text)
    if len(vf) < 7:
        errors.append(f"champs « Veille et vérification » mal lus dans le skill ({len(vf)})")
    for f in vf:
        if f not in data:
            errors.append(f"le champ {f} du skill manque dans portable/DATA.md")
    statuses = skill_statuses(skill_text)
    if len(statuses) < 9:
        errors.append("liste des statuts mal lue dans le skill")
    for st in statuses:
        if st not in compact:
            errors.append(f"le statut {st} du skill manque dans le prompt compact")
    pf = profile_fields(skill_text)
    if len(pf) < 12:
        errors.append(f"champs de config/profile mal lus dans le skill ({len(pf)})")
    for f in pf:
        if f not in profile:
            errors.append(f"le champ {f} de config/profile manque dans portable/PROFILE.md")
    if "config/profile" not in compact:
        errors.append("le prompt compact ne mentionne pas config/profile")
    check_page(skill_text, statuses, data, profile, errors)
    selftest = ROOT / "tests" / "agent" / "selftest.py"
    if selftest.exists():
        import subprocess
        r = subprocess.run([sys.executable, str(selftest)], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append("tests/agent/selftest.py échoue : " + (r.stdout.strip().splitlines() or ["?"])[-1][:140])
    tasks_dir = ROOT / "skills" / "recherche-emploi" / "references" / "taches"
    tpls = sorted(tasks_dir.glob("*.md")) if tasks_dir.exists() else []
    if len(tpls) < 3:
        errors.append("modèles de tâches planifiées manquants dans skills/recherche-emploi/references/taches/")
    documented = set(re.findall(r"`(\{\{[A-Z_]+\}\})`", skill_text))
    for tpl in tpls:
        txt = tpl.read_text(encoding="utf-8")
        if f"references/taches/{tpl.name}" not in skill_text:
            errors.append(f"le skill ne cite pas references/taches/{tpl.name}")
        for var in sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", txt))):
            if var not in documented:
                errors.append(f"{tpl.name} : la variable {var} n'est pas documentée dans le skill (§4)")
        for f in ("config/profile", "config/match_grid"):
            if tpl.name != "verification.md" and f not in txt:
                errors.append(f"{tpl.name} ne lit pas {f}")
        desc = re.search(r'^description: "(.*)"$', skill_text, flags=re.M)
    if not desc or len(desc.group(1)) > 1024:
        errors.append("description du skill absente ou de plus de 1024 caractères")
    for e in errors:
        print("ERREUR :", e)
    if not errors:
        print(f"OK : AGENTS.md à jour, prompt compact {len(compact)}/{COMPACT_LIMIT} caractères, poids, "
              f"{len(fields)} champs, {len(statuses)} statuts, {len(pf)} champs de profil et la page du Radar en phase")
    return 1 if errors else 0


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        sys.exit(check())
    OUT.write_text(build(), encoding="utf-8")
    print(f"écrit {OUT.relative_to(ROOT)} ({OUT.stat().st_size} octets)")
