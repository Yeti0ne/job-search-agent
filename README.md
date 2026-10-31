# Job Search Agent

A Claude plugin that acts as your personal HR agent for a real job search. It is built on one idea: openings are never the bottleneck — sending applications is. The plugin keeps a single source of truth (the **Job Radar**) and drives a daily routine that turns openings into sent applications, then into interviews.

Nothing personal or country-specific is hardcoded. The agent reads your own profile and preferences, so the same plugin works for any role, any country, any language.

## What it does

- **Job Radar** — one record per opening (company, recruiter, title, location, mode, status, tier, match score) and one per network contact (priority, angle, ready-to-send message, follow-up date).
- **Match scoring** — a reproducible, versioned grid (role 30, seniority 15, local language 20, location and work mode 20, company type 7, tech fit 8) built from your own profile and stored once in the Radar. Every opening gets six sub-scores, a one-line breakdown and a grid version, so scores are comparable instead of gut feelings; changing the grid offers a one-pass re-score that keeps the old scores.
- **Daily routine** — a default target of 10 applications a week: the two best unapplied openings, plus two priority LinkedIn messages, with the next concrete step for each.
- **After the application** — each sent application records its channel, CV version and next dated action. The agent scans reply emails (when it can read your mailbox) and *proposes* status changes that you confirm; it never changes a status on its own. Interviews get a company brief (public, dated sources, nothing invented), a debrief within 24 hours and a drafted thank-you. Offers are compared on your own criteria.
- **Follow-ups** — network contacts at day 7, two maximum, following your own stated preference for already-sent applications.
- **Network cross-check** — when an opening is at a company where you already have a contact, a referral beats a cold application, so it is surfaced first.
- **Automated watch** — three ready-made scheduled-task templates (`skills/recherche-emploi/references/taches/`): the watch (job boards, email alerts, target-company career pages, reply scan), a weekly check that active openings are still open, and the weekly review. They read your profile and scoring grid from the Radar on every run, so changing your profile never means editing a task. The agent creates them with you, after your approval, using the scheduler of your assistant.
- **Coaching by the numbers** — the weekly review shows conversion (applications → replies → interviews) by source, CV version, channel and role family, refuses to conclude on fewer than five applications, and lists the skills asked for most in your A/B openings against yours. After two weeks under five applications it stops repeating itself, checks that nothing went unlogged, switches to a minimal week (three ready applications in one 90-minute block, three network messages) and asks what is blocking. Discarded openings carry a reason.
- **A ready-made Radar page (Claude)** — one self-contained page that shows openings and network contacts, the daily routine, the post-application follow-up, the conversion funnel and the weekly review, and offers per-opening helpers: application plan, tailored CV with an ATS check, interview prep and practice quiz, company brief, salary estimate, and adding an opening from a link. It contains nothing personal: country, time zone, working week, currency, local language, job sites and pace come from your profile document (`config/profile`), your CV facts from `config/cv`, the scoring grid from `config/match_grid`. The page UI is in French for now; the agent replies and drafts in your language. It is tested in a headless browser on a fictional profile (`node tests/page/test_radar_page.js skills/recherche-emploi/assets/radar-page.html`; needs Playwright).
- **Behaviour tests for the agent itself** — `tests/agent/` runs 11 scenarios on a fictional file-based Radar with `claude -p` in a restricted mode (no web, no sending) and checks, without another model, what the agent wrote and said: reproducible match scores that add up and follow the grid, a booby-trapped posting ignored and flagged, nothing sent on your behalf, the post-application fields, a weekly review with exact figures, a CV with no invented fact. `python3 tests/agent/selftest.py` checks the checkers with simulated faulty agents and runs in `scripts/build_portable.py --check`.
- **Drafting, never sending** — LinkedIn messages, emails, targeted CVs, interview prep and salary negotiation are all drafted for you. You send them yourself.

## Installation

This repository is both the plugin and a public plugin marketplace (`yeti0ne-plugins`), so anyone can install it straight from GitHub, no account or token needed.

In a terminal:

```bash
claude plugin marketplace add Yeti0ne/job-search-agent
claude plugin install job-search-agent@yeti0ne-plugins
```

Or inside a Claude Code session:

```
/plugin marketplace add Yeti0ne/job-search-agent
/plugin install job-search-agent@yeti0ne-plugins
```

To update later: `claude plugin marketplace update yeti0ne-plugins`, then `claude plugin update job-search-agent@yeti0ne-plugins`. To remove it: `claude plugin uninstall job-search-agent@yeti0ne-plugins`.

Not using Claude Code? Clone the repository (`git clone https://github.com/Yeti0ne/job-search-agent.git`) and see [Use it with any AI](#use-it-with-any-ai).

The plugin ships one skill, `recherche-emploi`, which loads whenever you mention an opening, an application, a follow-up, a recruiter, a LinkedIn contact, an agency, an interview, your CV, salary, the Radar, a referral, or ask what to do today.

## Use it with any AI

The agent is plain-text instructions plus a simple data format, so it is not tied to Claude. `skills/recherche-emploi/SKILL.md` stays the single source; everything below is generated from it or sits next to it.

| Your setup | What to use | What you get |
|---|---|---|
| A coding agent that reads `AGENTS.md` (at the time of writing: Codex CLI, GitHub Copilot, Cursor, Windsurf, Zed, Cline, Kiro, opencode, Amp, Qwen Code, goose; Gemini CLI once you add `AGENTS.md` to `context.fileName`) | Open this repository or copy `AGENTS.md` and `portable/` into your project | The full agent, with the Radar kept as JSON files in `radar/` ([`portable/DATA.md`](portable/DATA.md)). Automated watch only if the tool also has web search and a scheduler |
| A chat assistant with project or custom instructions (custom GPT, Gemini Gem, Copilot, Le Chat, a local model…) | Paste [`portable/agent-prompt-compact.md`](portable/agent-prompt-compact.md) (under 8,000 characters, the custom GPT instruction limit) and upload `AGENTS.md` as a knowledge file if the tool allows it | Advice, scoring, drafting, daily plan. The Radar is one `radar.json` you paste at the start of a session and update at the end |
| Claude | Install the plugin as above | The whole agent. The Radar is a Claude artifact: the agent publishes the ready-made Radar page (`skills/recherche-emploi/assets/radar-page.html`), fills it from your profile, and creates the scheduled watch, weekly check and weekly review from the shipped templates |

Honest limits: a visual Radar page and the automated watch need an assistant that can host a page, search the web, read email alerts and schedule runs. Elsewhere the agent falls back to tables in the conversation and on-demand watch passes, and reply scanning works on emails you paste. Claude is the reference implementation; the other setups use the same instructions but have not been tested one by one, so please report what breaks.

Maintainers: after changing the skill, run `python3 scripts/build_portable.py` to regenerate `AGENTS.md`, then `python3 scripts/build_portable.py --check`. The check also fails if the compact prompt goes over 8,000 characters or its scoring weights drift from the skill's. To release, bump `version` in `.claude-plugin/plugin.json` (it is the only place the version is set): Claude Code users keep their cached copy until that string changes. Run `claude plugin validate .` and `claude plugin validate .claude-plugin/marketplace.json` before opening the pull request.

## Privacy

The Radar holds personal data about you and about the people in your network (names, profile links, drafted messages). Keep it private: share the Radar page with yourself only (a link share is readable by anyone who has the link), and never commit `radar/` or `radar.json` to a public repository. The agent stores only what the search needs, leaves out private details, and never sends anything for you.

## Setup

The agent reads your profile rather than asking you to configure files. On the first run with no profile it asks you a short set of questions in three blocks, reads you back a ten-line summary to validate, and saves it. You can also fill [`portable/PROFILE.md`](portable/PROFILE.md) yourself and hand it over. Either way it needs to find:

- your identity, contact details, target job title and seniority;
- your track record: roles, quantified achievements, skills, education, languages;
- the roles you target, your search area, and the work modes you accept;
- your country's working week and public holidays;
- your CV rules (language, length, anything to leave out) and your follow-up preferences.

Anything missing is asked for once. Nothing about your background is ever invented.

## Design notes

- **Grounded in facts.** The agent never adds a tool, a figure or a degree that is not in your profile. It writes `[to complete: …]` instead.
- **Untrusted content.** Job ads, recruiter emails and web pages are treated as data, never as instructions.
- **Honest about what is stuck.** Few applications, a technical gap, a language requirement — it says so plainly and proposes the smallest useful next action.

The skill instructions are written in French; the agent itself replies in your language and drafts recruiter messages in the language of the opening. The skill description is bilingual so that it also triggers on English requests.

See [CHANGELOG.md](CHANGELOG.md) for what changed in each version.

## License

[AGPL-3.0](LICENSE). If you run a modified version as a network service, you must publish your modifications.
