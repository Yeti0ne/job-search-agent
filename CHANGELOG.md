# Changelog

Versions follow `.claude-plugin/plugin.json`. Claude Code users only receive an update when that number changes.

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
