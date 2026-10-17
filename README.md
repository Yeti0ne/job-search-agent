# Job Search Agent

A Claude plugin that acts as your personal HR agent for a real job search. It is built on one idea: openings are never the bottleneck — sending applications is. The plugin keeps a single source of truth (the **Job Radar**) and drives a daily routine that turns openings into sent applications, then into interviews.

Nothing personal or country-specific is hardcoded. The agent reads your own profile and preferences, so the same plugin works for any role, any country, any language.

## What it does

- **Job Radar** — one record per opening (company, recruiter, title, location, mode, status, tier, match score) and one per network contact (priority, angle, ready-to-send message, follow-up date).
- **Match scoring** — a reproducible grid (role and seniority, local language, location and work mode, company type, tech fit) so openings get comparable scores instead of gut feelings.
- **Daily routine** — a default target of 10 applications a week: the two best unapplied openings, plus two priority LinkedIn messages, with the next concrete step for each.
- **Follow-ups** — network contacts at day 7, two maximum, following your own stated preference for already-sent applications.
- **Network cross-check** — when an opening is at a company where you already have a contact, a referral beats a cold application, so it is surfaced first.
- **Automated watch** — scheduled passes over job boards and email alerts, with a notification only for a strong match, plus a weekly review.
- **Drafting, never sending** — LinkedIn messages, emails, targeted CVs, interview prep and salary negotiation are all drafted for you. You send them yourself.

## Installation

Install the packaged plugin (`.plugin` file) from the Claude desktop app, or clone this repository into your plugin directory:

```bash
git clone https://github.com/Yeti0ne/job-search-agent.git
```

The plugin ships one skill, `recherche-emploi`, which loads whenever you mention an opening, an application, a follow-up, a recruiter, a LinkedIn contact, an agency, an interview, your CV, salary, the Radar, a referral, or ask what to do today.

## Setup

The agent reads your profile rather than asking you to configure files. Before your first real session, make sure it can find:

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

The skill instructions are written in French; the agent itself replies in your language and drafts recruiter messages in the language of the opening.

## License

[AGPL-3.0](LICENSE). If you run a modified version as a network service, you must publish your modifications.
