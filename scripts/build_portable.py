#!/usr/bin/env python3
"""Génère AGENTS.md et AGENTS.en.md (version portable, tout assistant IA) depuis le skill.

Sources : skills/recherche-emploi/SKILL.md (référence, français) et SKILL.en.md (version anglaise)
Sorties : AGENTS.md = portable/adapter-preamble.md + corps du skill (sans l'en-tête YAML)
          AGENTS.en.md = portable/adapter-preamble.en.md + corps de SKILL.en.md

Usage :
  python3 scripts/build_portable.py           écrit AGENTS.md
  python3 scripts/build_portable.py --check   échoue si AGENTS.md n'est pas à jour, si le prompt
                                              compact dépasse 8000 caractères (limite des
                                              instructions d'un GPT personnalisé) ou si ses poids
                                              de notation diffèrent de ceux du skill, ou si les champs,
                                              statuts et champs de profil du skill ne se retrouvent pas
                                              dans le prompt compact, DATA.md et PROFILE.md,
                                              et si la version anglaise (SKILL.en.md, AGENTS.en.md, prompt compact,
                                              PROFILE.en.md, DATA.en.md, modèles de tâches .en.md) reste en phase avec le français
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
SKILL_EN = ROOT / "skills" / "recherche-emploi" / "SKILL.en.md"
PREAMBLE_EN = ROOT / "portable" / "adapter-preamble.en.md"
COMPACT_EN = ROOT / "portable" / "agent-prompt-compact.en.md"
DATA_EN = ROOT / "portable" / "DATA.en.md"
PROFILE_EN = ROOT / "portable" / "PROFILE.en.md"
OUT_EN = ROOT / "AGENTS.en.md"
COMPACT_LIMIT = 8000


def build(lang: str = "fr") -> str:
    skill_file, preamble_file = (SKILL, PREAMBLE) if lang == "fr" else (SKILL_EN, PREAMBLE_EN)
    skill = skill_file.read_text(encoding="utf-8")
    body = re.sub(r"\A---\n.*?\n---\n", "", skill, count=1, flags=re.S).lstrip("\n")
    body = re.sub(r"\A<!--.*?-->\n+", "", body, count=1, flags=re.S)
    return preamble_file.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + body.rstrip("\n") + "\n"


def ident_list(seg: str):
    """Noms de champs d'une énumération « a (…), b et c (…) » : premier mot de chaque élément, parenthèses retirées."""
    for _ in range(3):
        seg = re.sub(r"\([^()]*\)", "", seg)
    seg = re.sub(r"\{[^{}]*\}", "", seg)
    out = []
    for piece in re.split(r",| et | and ", seg):
        w = piece.strip().split(" ")[0] if piece.strip() else ""
        if re.fullmatch(r"[a-z]+(?:_[a-z]+)*", w) and w not in ("and", "et", "if", "or", "when"):
            out.append(w)
    return out


def en_lists(text: str):
    """Mêmes listes que le français, lues dans SKILL.en.md."""
    def seg(pattern):
        m = re.search(pattern, text, flags=re.S)
        return ident_list(m.group(1)) if m else []
    return {
        "after": seg(r"After applying: (.*?)\. Generated texts"),
        "watch": seg(r"Watch and verification: (.*?)\. After applying"),
        "statuses": seg(r"(?m)^- Statuses \(stored values\): ([^\n]*)\.$"),
        "profile": ident_list(balanced(text, "the document `config/profile` (fields: ") or ""),
        "cv": ident_list(balanced(text, "the document `config/cv` (fields: ") or ""),
    }


def fr_lists(text: str):
    return {
        "after": skill_fields(text), "watch": skill_fields_veille(text), "statuses": skill_statuses(text),
        "profile": profile_fields(text), "cv": cv_fields(text),
    }


def norm_tokens(text: str):
    """Éléments entre accents graves, avec les noms de fichiers anglais ramenés aux noms français et les {variables} neutralisées."""
    t = text.replace(".en.md", ".md")
    toks = set()
    for tok in re.findall(r"`([^`\n]+)`", t):
        toks.add(re.sub(r"\{[^{}]*\}", "{}", tok))
    return toks


def check_onboarding(errors, fr_skill_text, en_skill_text, compact_fr, compact_en):
    """Le questionnaire d'accueil (premier lancement) doit exister dans les deux langues, avec les mêmes quatre étapes."""
    for lang, skill, compact, key in (("fr", fr_skill_text, compact_fr, "questionnaire d'accueil"), ("en", en_skill_text, compact_en, "welcome questionnaire")):
        tag = "" if lang == "fr" else "[en] "
        block = skill.split("\n\nThe scheduled tasks")[0] if lang == "en" else skill.split("\n\nLes tâches planifiées")[0]
        start = block.find("**Premier lancement" if lang == "fr" else "**First run")
        block = block[start:] if start >= 0 else ""
        if key not in block:
            errors.append(f"{tag}SKILL{'' if lang == 'fr' else '.en'}.md : le questionnaire d'accueil du premier lancement est absent")
            continue
        steps = re.findall(r"^\d\. \*\*", block, flags=re.M)
        if len(steps) != 4:
            errors.append(f"{tag}le questionnaire d'accueil doit avoir 4 étapes numérotées, trouvé {len(steps)}")
        yes_no = len(re.findall(r"^\s+- \*(?:Oui|Non|Yes|No)\*", block, flags=re.M))
        if yes_no != 2:
            errors.append(f"{tag}le questionnaire doit couvrir les deux cas « a un CV » et « n'a pas de CV », trouvé {yes_no}")
        for needle in (("[à compléter" if lang == "fr" else "[to complete"), ("jamais une instruction" if lang == "fr" else "never an instruction"), "PROFILE"):
            if needle not in block:
                errors.append(f"{tag}le questionnaire d'accueil ne contient pas « {needle} »")
        if not all(f"{i})" in compact for i in (1, 2, 3, 4)) or ("CV" not in compact):
            errors.append(f"{tag}le prompt compact doit décrire le questionnaire d'accueil en 4 étapes (1) à 4))")


def check_english(errors, fr_skill_text: str):
    """Garde la version anglaise en phase avec le français : mêmes sections, poids, champs, statuts, variables, éléments de code."""
    for f in (SKILL_EN, PREAMBLE_EN, COMPACT_EN, DATA_EN, PROFILE_EN):
        if not f.exists():
            errors.append(f"[en] {f.relative_to(ROOT)} est introuvable")
            return
    if not OUT_EN.exists() or OUT_EN.read_text(encoding="utf-8") != build("en"):
        errors.append("[en] AGENTS.en.md n'est pas à jour : lancer python3 scripts/build_portable.py")
    en = SKILL_EN.read_text(encoding="utf-8")
    compact = COMPACT_EN.read_text(encoding="utf-8")
    if len(compact) > COMPACT_LIMIT:
        errors.append(f"[en] portable/agent-prompt-compact.en.md fait {len(compact)} caractères (limite {COMPACT_LIMIT})")
    nums = lambda s: re.findall(r"\d+", s or "")
    w_fr, w_en = weights(fr_skill_text), weights(en)
    if not w_en or nums(w_fr) != nums(w_en):
        errors.append(f"[en] poids de notation différents dans SKILL.en.md : {w_en!r} (français : {w_fr!r})")
    if not w_en or w_en not in compact:
        errors.append("[en] le prompt compact anglais n'a pas les mêmes poids que SKILL.en.md")
    heads = lambda s: re.findall(r"^## (\d+)\.", s, flags=re.M)
    if heads(fr_skill_text) != heads(en):
        errors.append(f"[en] sections numérotées différentes : {heads(en)} (français : {heads(fr_skill_text)})")
    if len(re.findall(r"^## ", fr_skill_text, flags=re.M)) != len(re.findall(r"^## ", en, flags=re.M)):
        errors.append("[en] nombre de sections « ## » différent entre SKILL.md et SKILL.en.md")
    a, b = fr_lists(fr_skill_text), en_lists(en)
    for k in a:
        if a[k] != b[k]:
            errors.append(f"[en] liste « {k} » différente : seulement FR {sorted(set(a[k]) - set(b[k]))}, seulement EN {sorted(set(b[k]) - set(a[k]))}")
    ta, tb = norm_tokens(fr_skill_text), norm_tokens(en)
    if ta != tb:
        errors.append(f"[en] éléments de code différents entre SKILL.md et SKILL.en.md : FR seul {sorted(ta - tb)[:6]}, EN seul {sorted(tb - ta)[:6]}")
    data_en, profile_en = DATA_EN.read_text(encoding="utf-8"), PROFILE_EN.read_text(encoding="utf-8")
    for f in a["after"] + a["watch"]:
        if f not in data_en:
            errors.append(f"[en] le champ {f} manque dans portable/DATA.en.md")
        if f in a["after"] and f not in compact:
            errors.append(f"[en] le champ {f} manque dans le prompt compact anglais")
    for st in a["statuses"]:
        if st not in compact:
            errors.append(f"[en] le statut {st} manque dans le prompt compact anglais")
    for f in a["profile"]:
        if f"`{f}`" not in profile_en or f'"{f}"' not in profile_en:
            errors.append(f"[en] le champ {f} de config/profile manque dans portable/PROFILE.en.md (liste ou exemple JSON)")
    for f in a["cv"]:
        if f not in profile_en or f not in data_en:
            errors.append(f"[en] le champ {f} de config/cv manque dans PROFILE.en.md ou DATA.en.md")
    keys = lambda p: set(re.findall(r'"([A-Za-z_]+)"\s*:', p.read_text(encoding="utf-8")))
    for fr_f, en_f in ((DATA, DATA_EN), (PROFILE, PROFILE_EN)):
        if keys(fr_f) != keys(en_f):
            errors.append(f"[en] clés JSON des exemples différentes entre {fr_f.name} et {en_f.name} : {sorted(keys(fr_f) ^ keys(en_f))[:8]}")
        h = lambda p: len(re.findall(r"^## ", p.read_text(encoding="utf-8"), flags=re.M))
        if h(fr_f) != h(en_f):
            errors.append(f"[en] nombre de sections différent entre {fr_f.name} et {en_f.name}")
    if "config/profile" not in compact:
        errors.append("[en] le prompt compact anglais ne mentionne pas config/profile")
    tasks_dir = ROOT / "skills" / "recherche-emploi" / "references" / "taches"
    for fr_t in sorted(p for p in tasks_dir.glob("*.md") if not p.name.endswith(".en.md")):
        en_t = fr_t.with_name(fr_t.stem + ".en.md")
        if not en_t.exists():
            errors.append(f"[en] {en_t.name} manque")
            continue
        if f"references/taches/{en_t.name}" not in en:
            errors.append(f"[en] SKILL.en.md ne cite pas references/taches/{en_t.name}")
        tf, te = fr_t.read_text(encoding="utf-8"), en_t.read_text(encoding="utf-8")
        if set(re.findall(r"\{\{[A-Z_]+\}\}", tf)) != set(re.findall(r"\{\{[A-Z_]+\}\}", te)):
            errors.append(f"[en] {en_t.name} : variables {{{{…}}}} différentes du français")
        steps = lambda s: len(re.findall(r"^(?:\d+\.|[a-c]\))", s, flags=re.M))
        if steps(tf) != steps(te):
            errors.append(f"[en] {en_t.name} : nombre d'étapes différent ({steps(te)} contre {steps(tf)})")
        ft, fe = norm_tokens(tf), norm_tokens(te)
        if ft != fe:
            errors.append(f"[en] {en_t.name} : éléments de code différents : FR seul {sorted(ft - fe)[:5]}, EN seul {sorted(fe - ft)[:5]}")


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


def balanced(text: str, marker: str):
    """Contenu de la parenthèse qui suit `marker` (parenthèses imbriquées comprises), ou None."""
    i = text.find(marker)
    if i < 0:
        return None
    j, depth = i + len(marker), 1
    while j < len(text) and depth:
        depth += {"(": 1, ")": -1}.get(text[j], 0)
        j += 1
    return text[i + len(marker):j - 1] if depth == 0 else None


def profile_fields(text: str):
    seg = balanced(text, "le document `config/profile` (champs : ")
    return ident_list(seg) if seg else []


def cv_fields(text: str):
    seg = balanced(text, "le document `config/cv` (champs : ")
    return ident_list(seg) if seg else []


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
        if f"`{f}`" not in profile or f'"{f}"' not in profile:
            errors.append(f"le champ {f} de config/profile manque dans portable/PROFILE.md (liste ou exemple JSON)")
    if "config/profile" not in compact:
        errors.append("le prompt compact ne mentionne pas config/profile")
    check_page(skill_text, statuses, data, profile, errors)
    check_english(errors, skill_text)
    if SKILL_EN.exists() and COMPACT_EN.exists():
        check_onboarding(errors, skill_text, SKILL_EN.read_text(encoding="utf-8"), compact, COMPACT_EN.read_text(encoding="utf-8"))
    selftest = ROOT / "tests" / "agent" / "selftest.py"
    if selftest.exists():
        import subprocess
        r = subprocess.run([sys.executable, str(selftest)], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append("tests/agent/selftest.py échoue : " + (r.stdout.strip().splitlines() or ["?"])[-1][:140])
    tasks_dir = ROOT / "skills" / "recherche-emploi" / "references" / "taches"
    tpls = sorted(p for p in tasks_dir.glob("*.md") if not p.name.endswith(".en.md")) if tasks_dir.exists() else []
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
    for out, lang in ((OUT, "fr"), (OUT_EN, "en")):
        out.write_text(build(lang), encoding="utf-8")
        print(f"écrit {out.relative_to(ROOT)} ({out.stat().st_size} octets)")
