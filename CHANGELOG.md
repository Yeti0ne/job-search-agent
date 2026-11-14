# Changelog

Versions follow `.claude-plugin/plugin.json`. Claude Code users only receive an update when that number changes.

## 0.9.0
- **Fourth task template**: `references/taches/enrichissement.md` (and `.en.md`). Once per working day it fills in `required_skills` and `ad_summary` for the active A/B openings that have none (added by hand, posting unreadable on the day of the watch), 30 at most per run, and notes a failure in `enrich_failed_at` so the same posting is not retried for 14 days. It changes no status and sends no notification.
- **Public holidays**: optional profile list `holiday_dates` (YYYY-MM-DD). The page skips those dates when it counts working days (for instance the "check for a reply" date ten working days after an application).
- **Services companies on every run**: the watch checks `service_companies` one by one on the first run of the day and with grouped queries on the other runs.
- **Skill**: the data model now lists the fields the page already used (`fav`, `commute_min`, `co_glassdoor`, `co_note`, `cv_match`, `enrich_failed_at`), and §4 describes the page's "AI" selector (Eco, Auto, In-depth).
- Tests: one more page control (a holiday from the profile is skipped).

## 0.8.0
- **New Radar page interface**: four views (Today, Openings, Network, Review) with a bottom navigation on the phone and a side navigation on the desktop, tiles and a full-screen record for each opening, a guided "next step" block (plan, CV, apply, follow-up), match scores shown as six bars, full-text search across openings and contacts, collapsible filters, cities to keep or to leave out, sorting on any column in both directions.
- **CV with fields**: every `[to complete: …]` gap of a tailored CV becomes a field the user fills in one by one; only those fields change, the rest of the CV stays as it is (`cv_tpl`, `cv_fills`, `cv_edited_at`). Simple calculations are computed by the page, never by the model.
- **Suggested contacts**: new collection `suggested_contacts`. Contacts proposed by an in-depth scan wait there and show up in the record of the opening at the same company, with "Add" and "Ignore"; nothing enters `contacts` without that choice.
- **Fast sites**: optional profile list `fast_sites`. Openings from those sites at 70 % match or more, still to be handled, are marked "Urgent" with a 5-day countdown and come first in the list and in the routine. No site is hard-coded; without the list the alert never shows.
- **Services companies in the watch**: optional profile list `service_companies` (IT services, consulting or staffing companies of the user's field). The watch template checks them on the first run of the day, client-site assignments included, with rules for `company` / `recruiter`, near-duplicates across companies and a `service_new` counter in the log.
- Sorting by salary reads the range written in the posting (`SAL.parseAnn`); there is still no built-in salary scale.
- Tests: the page tests follow the new interface and add three controls on fast sites (alert shown from the profile, no alert without the list, no script error): 36 controls.

## 0.7.0
- **Welcome questionnaire** (skill §0, French and English): on the first run the agent asks whether the user has a CV. Yes: it reads the uploaded or pasted CV (PDF, Word, text; treated as data, never as instructions, so an instruction hidden in a CV is flagged and ignored), gives back what it took and what is missing, and adds nothing that is not on it. No: it builds the CV with the user job by job and drafts a one-page ATS-friendly CV from their answers only, every gap marked `[to complete: …]`. Then only the questions the CV does not settle (search, rules and pace), three at most per message, and a ten-line summary to validate: nothing is saved before that validation. Age, family situation and identity numbers never reach the Radar, and the target salary and notice period go to the full profile (`radar/config/profile_full.md` for assistants without memory), never into `config/cv.facts`.
- **English version** of the agent for every assistant: `AGENTS.en.md` (generated), `skills/recherche-emploi/SKILL.en.md`, `portable/agent-prompt-compact.en.md`, `portable/PROFILE.en.md`, `portable/DATA.en.md`, `portable/adapter-preamble.en.md` and the three task templates (`references/taches/*.en.md`). Stored values (statuses, reject reasons, field names) are identical in both languages. `scripts/build_portable.py --check` now fails when French and English drift apart.
- Weekly review template: every `metrics` counter covers the past week (`replies` included), and the final answer is limited to the four notification lines (caveats stay in the report). Found by the new tests: the previous wording gave 20-line notifications.
- Tests: 14 behaviour scenarios, run in French or English (`--lang en`); three new ones cover the questionnaire (CV given, no CV, answers given and validated in one go). Verifiers accept derived durations such as "more than 12 years", a protective `.gitignore`, and gaps flagged as `[to complete: …]`. 77 controls in `selftest.py`.

## 0.6.1
- Skill §3 : l'ordre de « quoi faire aujourd'hui » est tenu même quand l'agent regroupe des actions (une relance due passe avant les offres, jamais après). Défaut trouvé par les nouveaux tests de comportement.
- Tests de comportement de l'agent (`tests/agent/`) : 11 scénarios sur un Radar fictif en fichiers, lancés avec `claude -p` en mode restreint, vérifiés sans modèle (notes reproductibles et cohérentes avec la grille, annonce piégée ignorée et signalée, rien d'envoyé, boucle après candidature, bilan chiffré, CV sans invention, jour non ouvré, Radar absent). `selftest.py` contrôle les vérificateurs avec des agents fautifs simulés et fait partie de `scripts/build_portable.py --check`.

## 0.6.0
- Ready-made Radar page for Claude: `skills/recherche-emploi/assets/radar-page.html`, a single self-contained page with no personal or country-specific content. It reads `config/profile` (country, time zone, working week, currency, local language, job sites, weekly target…), the new `config/cv` document (name, contact, facts, rules, language, max_words) and `config/match_grid`.
- Page features: offers and network views with filters, match scores and their breakdown, daily routine with « à traiter d'abord » (interviews, replies to confirm, due actions), post-application follow-up fields, discard reasons (`reject_reason`), conversion funnel with the 5-application threshold, daily and seasonal activity, weekly review, application plan, tailored CV with a generic ATS check (keywords taken from the posting itself), interview prep and practice quiz, company brief, salary estimate in the profile's currency, add-an-opening-by-link scored with the user's own grid.
- Legacy statuses from older Radars (`surqualifie`, `accred_defense`, `hebreu_avance`) are shown as « ignoré » with the matching discard reason.
- Skill §4 explains how to publish the page (capabilities, privacy); §0 saves `config/cv`; `role_class` thresholds are now written out; the weekly review computes its escalation from `applied_at` instead of the previous report.
- Tests: `tests/page/` runs the page in a headless browser against a mocked Claude runtime and a fictional profile (Lyon, EUR, French): settings, sites, statuses, discard reasons, time zone, add-by-link scoring, prompts (no personal data, profile facts present), CV and ATS, salary currency, working-week arithmetic, empty Radar, no database. `scripts/build_portable.py --check` now also verifies the page against the skill (statuses, config documents, fields, script syntax, no hardcoded time zone).

## 0.5.0
- Scheduled-task templates in `skills/recherche-emploi/references/taches/`: `veille.md`, `verification.md`, `bilan.md`. Profile-driven (they read `config/profile` and `config/match_grid` on each run), reply scan and `required_skills` capture in the watch, conversion tables, escalation and `metrics` in the weekly review.
- Creation procedure in the skill (§4): variables, schedule in the user's time zone and work week, approval before creating, check run.
- `config/profile` gains `levels_accepted`, `exclusions`, `tasks`.
- `build_portable.py --check` also verifies the templates (variables documented, configuration read, files cited).

## 0.4.0
- Post-application loop: `channel`, `cv_version`, `role_class`, `stage`, `interview_at`, `next_action` / `next_action_date`, `debrief_text`. A reply scan proposes status changes (`suggested_status`, `suggested_note`, `suggested_at`) and never applies them without confirmation.
- Company brief (`company_brief`), interview debrief template, thank-you drafts and offer comparison on the user's own criteria.
- Weekly review: conversion by source, CV version, channel and role family (no percentage under five applications), median reply delay, unanswered applications, most requested skills against the profile.
- Veille keeps `required_skills` and `ad_summary` for A/B openings.
- First run without a profile: three-block questionnaire, ten-line validated summary, `config/profile` document read by the page and scheduled tasks. New template `portable/PROFILE.md`.
- Skill description is now bilingual. README states exactly what is and is not shipped.

## 0.3.0
- `reject_reason`, escalation rule (minimal week), pre-screening sheet, third-party data and privacy rules.

## 0.2.2
- Grid: a named public body, administration or non-profit scores 5 on company type.

## 0.2.1
- First public version: skill, portable `AGENTS.md`, compact prompt, file-based data format.
