# Profile template

The agent assumes nothing: everything that depends on you, your trade or your country comes from this profile. Fill in what is useful, leave blank what you do not know yet (the agent will ask once), then give the file to the assistant at the start of the first session, or paste it into your project's instructions.

This file contains personal data: do not publish it and do not commit it to a public repository. Put no ID number, password, or health, family or financial information unrelated to the search.

You do not have to fill in this file yourself. On first launch, the agent first asks you one question: "Do you have a CV?". If so, you upload it (PDF, Word or pasted text) and it takes what it can from it; if not, it builds it with you, job by job, without inventing anything. It then asks only what your CV does not say (the blocks below), and reads you back a summary of about ten lines to validate before saving anything.

## Block 1: who you are and what you aim for
- First and last name, e-mail and phone to put on CVs and messages:
- Trade, seniority level (junior, mid, senior, manager, executive), market title that recruiters recognise:
- Background, most recent first: position, company, dates, and for each two or three quantified achievements (what you did, by how much, in how long):
- Skills, tools and certifications you are sure of:
- Education:
- Languages and levels (honest ones: the agent will never write a level you do not have):
- Known weak points or gaps that the agent must not hide, but prepare for:
- Target roles: main / secondary / adjacent (close to your trade, that you would accept):
- Accepted job levels (for example senior and mid-level, but not junior) and exclusions (types of roles to discard outright):
- Company types you prefer (start-up, large group, public, association, consulting…), and target companies by priority (A, B):
- Campaign goal: outreach, interviews, offer, deadline:

## Block 2: where and how you search
- Country and search area:
- Accepted modes: onsite / hybrid / remote (remote within the country only, or abroad too):
- Home (city, district) to compute commutes, departure time, means of transport. Only the city goes into the Radar's configuration:
- Maximum commute accepted, and cities ranked from most to least desirable (or "to set up with you"):
- The country's local language and your level (read / spoken / professional), learning tool or workbook if any:
- The country's working week (e.g. Monday to Friday, or Sunday to Thursday), public holidays (list or calendar to use):
- Time zone:
- Currency and how salary is quoted (gross monthly, gross annual…); target range, if you have one (an estimate, to check):
- Notice period or availability:
- Possible obstacles: work permit, nationality required, security clearance, local obligations:
- Job sites to watch in the country (leave blank to let the agent propose a list):
- Agencies, associations and helpful resources in the country:

## Block 3: your rules
- CV rules: language(s), maximum length, location to write (country only, city…), things to avoid:
- Follow-ups on applications already sent: never / after N days / only after a contact:
- Pace: number of applications per week (10 by default), days when you want nothing (other than public holidays):
- Notifications: only for an A or B opening and for a reply to confirm (default), or other:
- Working language with the agent, and language of messages to recruiters (the opening's language by default):
- Anything the agent must always or never do for you:

## What goes into the Radar (document `config/profile`)
Only what the page and the scheduled tasks need, with no contact details or background: `country`, `timezone`, `work_week`, `holidays`, `currency`, `local_language` (name and level), `modes`, `target_roles` (main, secondary, adjacent), `levels_accepted`, `exclusions`, `home_area` (the city only), `zone_scale` (city → points from 4 to 20), `job_sites`, `preferred_company_types`, `target_companies`, `weekly_target`, `followup_pref`, `notify`, `ui_language`, `tasks` (name and identifier of the scheduled tasks created). Fictional example:

```json
{
  "country": "France",
  "timezone": "Europe/Paris",
  "work_week": ["mon", "tue", "wed", "thu", "fri"],
  "holidays": "legal public holidays of France",
  "currency": "EUR",
  "local_language": { "name": "French", "level": "native" },
  "modes": ["hybrid", "remote"],
  "target_roles": { "main": ["IT Operations Manager"], "secondary": ["Infrastructure Project Manager"], "adjacent": ["Level 3 Support"] },
  "levels_accepted": ["senior", "mid"],
  "exclusions": ["pure sales", "level 1 support"],
  "home_area": "Lyon",
  "zone_scale": { "Lyon": 20, "Villeurbanne": 20, "Grenoble": 12, "Paris": 6 },
  "job_sites": ["LinkedIn", "Indeed", "Welcome to the Jungle", "APEC"],
  "preferred_company_types": ["scale-up", "mid-size company"],
  "target_companies": { "A": ["Example Inc."], "B": [] },
  "weekly_target": 10,
  "followup_pref": "no follow-up on an application already sent before 14 days",
  "notify": "ab_et_reponses",
  "ui_language": "en",
  "tasks": {}
}
```
(Fictional values: the agent fills in the real document from your profile, after your validation.) `local_language` can also carry `resource_url` (your workbook or learning app), and `job_sites` accepts names or objects `{ "name": "…", "url": "…" }`.

## What the Radar page also reads (document `config/cv`)
So that the page buttons (tailored CV, plan, interview preparation, salary estimate) work, the agent also writes a document `config/cv` from your block 1 and block 3: `name`, `contact` (e-mail, phone, city or country to write on the CV), `facts` (quantified background, skills, education, languages: only what is true), `rules` (your CV rules), `language` (CV language), `max_words` (maximum length). It is the only Radar document that holds your contact details: share the Radar with nobody but yourself.

```json
{
  "name": "Camille Martin",
  "contact": "camille.martin@example.org · +33 6 12 34 56 78 · Lyon",
  "facts": "IT Operations Manager. Example Inc. (2018-2026): team of 8, 99.9% availability. Skills: monitoring, incident management. Master's in computer science. Native French, fluent English.",
  "rules": "CV in English, one page, city only in the location line.",
  "language": "English",
  "max_words": 450
}
```
(Fictional values.)
