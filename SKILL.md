---
name: intelligent-outreach
description: Ethical participate-and-promote (P&P) outreach workflow for finding relevant public posts, comments, threads, and debates; drafting transparent contributions that both participate in the existing context and promote the user's article, video, specialist item, or website; preparing human review; and optionally posting only after exact approval. Use for community research, audience discovery, context-specific outreach drafts, non-spam promotion, credential-backed login, approval review, or approved posting. Do not use for autonomous posting, stealth marketing, account creation, ban evasion, mass messaging, scraping private spaces, impersonation, credential storage in files, or rule-breaking automation.
---

# Intelligent Outreach

## Overview

Use this skill to plan ethical **participate-and-promote (P&P)** outreach. Every outreach message must be a reply or comment in a relevant pre-existing public context and must do two things: participate in that context and transparently promote the selected item. The skill may research public conversations, draft replies, prepare secure credential-backed login, and post through an authorized account only after the user approves the exact target, account, and final message inside Codex chat.

## P&P Is the Core Model

**P&P message** means **participate-and-promote message**. It is the default unit of intelligent outreach, not an optional drafting style.

Participation uses a broad, practical standard. The stimulus may be a standalone post, an individual comment, a question, a thread, or a developed debate. It need not already contain disagreement or multiple participants. A message participates when it makes a meaningful, context-specific contribution to what already exists; merely mentioning the same broad topic does not qualify.

Choose the participation standard from the promoted item:

1. **Opinion-based or argumentative item**: contribute an actual argument. Identify a premise, claim, inference, distinction, objection, or conclusion in the target and respond with reasoning from or closely connected to the promoted item. Agreement may extend or refine the target; disagreement may question or rebut it. The message must remain substantively useful without its promotional link.
2. **Non-opinion specialist item**: contribute specialist discussion rather than forcing an argument. Explain, clarify, interpret, compare, contextualize, or answer something specific in the target using the promoted item's subject matter. The message must remain substantively useful without its promotional link.
3. **General website or platform**: use the contextual website exception. A brief, natural reply tied to the target is enough because a broad website cannot honestly supply a specialist argument for every relevant context. Acknowledge or lightly extend the target's point, then explain how the website reflects or collects relevant lives, voices, work, or experiences. This contribution may be small and need not stand alone as an argument, but it must be tailored, relevant, non-spammy, transparently affiliated, and attached to something pre-existing.

For example, under a post about young people in China rethinking marriage, a website-level reply may briefly note that changing lives and expectations are reshaping younger people's views, then introduce Inkstone as a place showing Chinese students' lives and voices. It need not manufacture a philosophical debate.

The website exception does not permit generic link dropping. Do not reuse the same lightly edited introduction across unrelated targets, start unsolicited standalone promotional posts, or claim relevance where the target has no concrete connection to the website's mission.

## Non-Negotiables

Read `references/outreach_policy.md` when the task involves live communities, controversial topics, account use, platform rules, login, or posting decisions.

Read `references/credential_and_review_flow.md` before setting up credentials, logging in, asking for approvals, or posting.

Always follow these constraints:

- Use only public pages, official APIs, approved exports, or user-provided materials.
- Do not create accounts, vote, follow, DM, or send private messages automatically.
- Do not log in or post unless the user explicitly asks for credential-backed execution and approves the exact target, account, and final message in Codex chat.
- Do not evade bans, captchas, rate limits, anti-bot systems, paywalls, moderation, or platform restrictions.
- If CAPTCHA, MFA, suspicious-login, or security-check UI appears, stop and ask the user to complete it manually.
- Do not impersonate neutral users, hide the user's affiliation, or pretend a recommendation is unaffiliated.
- Do not produce bulk generic comments. Every draft must respond to its specific target. Opinion-based and specialist-item P&P messages must add standalone value even if the link is removed; contextual website introductions must make at least a brief, tailored contribution before introducing the site.
- Do not target protected classes with manipulative, discriminatory, hateful, harassing, or demeaning content.
- Prefer fewer high-fit comments over high-volume posting.

If the user asks for autonomous posting, covert persuasion, or spam-like behavior, redirect to a human-reviewed outreach plan.

Do not use the word "propaganda" as an operating mode. Treat user requests for propaganda as requests for transparent outreach, advocacy, or promotion that must disclose affiliation and follow platform rules.

## Workflow

At the start of every session:

- Read `references/site_profile.md` for Inkstone's mission, current content, platform list, search strategy, and reply standards.
- Run `scripts/check_story_index.py` to compare the live `/stories` page with `references/story_index.md`. If the check cannot reach the site, report that freshness is unverified; for specific-item outreach, fetch and read the target article directly before proceeding.
- Read `references/story_index.md` to understand the current article archive. If the live check finds a new article, fetch and read it fully, add its entry, and update the count and date before proceeding. Do not draft outreach for an article you have not read.
- If new articles appear on the site that are not yet in the index, add their entries at the end of the relevant series section and update the "Last updated" and "Total stories" fields.
- Read `memory/outreach_log.md` before searching for communities so you know what has already been covered.

1. Clarify the offer:
   - Identify the article, video, website, or thesis being promoted.
   - Classify it as `opinion-based`, `non-opinion specialist`, or `general website`, and apply the matching P&P participation standard above.
   - Summarize why it is relevant, who benefits, and what the user can honestly disclose about ownership or affiliation.
   - Ask for missing essentials only when they cannot be inferred: target topic, URL, audience, platforms, and posting account constraints.
   - Read `references/site_profile.md` before proceeding. This file describes the site's mission, current content, and search strategy. Use it to determine what kind of communities are genuinely relevant to this session's goal.
   - Read `references/story_index.md` to understand what articles exist. If promoting a specific article, verify it has an entry in the index. If not, fetch and read the article in full, then add its entry to the index before continuing. Do not draft outreach for any article you have not read.

2. Prepare credential storage if posting may be requested:
   - Use `scripts/credential_store.py status` to identify a supported local secret backend.
   - Prefer OS or password-manager storage. On macOS, ask permission to launch `scripts/credential_store.py set-gui <platform>` when credentials are missing. The user enters the username and hidden password in native dialogs; Codex receives only success or cancellation.
   - If the username is already known, pass it with `--username <username>` so only the hidden-password dialog appears.
   - Use `scripts/credential_store.py set <platform> --username <username>` only as a terminal fallback.
   - Never ask the user to paste passwords into Codex chat. Never store credentials in `SKILL.md`, `.env`, JSON, YAML, shell history, screenshots, or git-tracked files.
   - If no supported secure store is available, stop and ask the user to install or configure one.

2.5. Set the execution mode:
   - Choose one mode: `research-only`, `draft-only`, or `approved-posting`.
   - Before selecting `approved-posting`, verify that a controlled browser or official posting API is available, the user-authorized account exists, the platform permits the intended automation, and either an authenticated browser session, native password autofill, or a sealed credential-aware adapter is available.
   - If only generic browser control is available, do not retrieve Keychain secrets through model-visible tool output. Ask the user to complete login manually, then continue with the authenticated session.
   - If any posting capability check fails, downgrade to `draft-only` and state what is missing. Never imply that posting is available merely because this skill describes the procedure.

3. Find candidate communities:
   - Search public web results, platform search pages, official APIs, or user-provided links.
   - Treat relevant standalone posts, individual comments, questions, threads, and debates as valid stimuli. Do not require an established multi-person discussion.
   - For opinion-based items, require a rationally discussable claim that the item can answer, extend, refine, or rebut.
   - For non-opinion specialist items, require a concrete question, fact, practice, experience, interpretation, or subject that supports useful specialist engagement.
   - For a general website, require a concrete contextual connection to the site's mission or audience; a brief tailored acknowledgment is sufficient and an argument is not required.
   - Capture candidate URL, platform, community or thread title, topic, visible rules, moderation notes, thread context, last activity if visible, and why it appears relevant.
   - Avoid private groups, invite-only spaces, DMs, and communities whose rules prohibit self-promotion or automated outreach.
   - Use the platform list and search strategy in `references/site_profile.md` Section 3. Always search the standing platform list, then expand based on what is being promoted in this session. The session-specific expansion should reflect the intellectual or thematic fit of the specific item, not just surface keyword overlap.

4. Score candidates:
   - Use `scripts/score_candidates.py` when the candidate list is structured as JSON.
   - Prefer candidates with direct topical overlap, active discussion, explicit rule compatibility, and a clear way to contribute without derailing the thread.
   - Flag legal, ethical, reputational, or moderation risks.

4.5. Check prior outreach:
   - Before drafting for a candidate, check `memory/outreach_log.md` for the same item and community or thread.
   - Skip the target if the same item was already promoted there, unless the prior entry is more than six months old and the thread remains active.

5. Draft replies:
   - Write in the voice of a transparent participant, not a disguised advertiser.
   - Start by addressing the thread's actual point.
   - Apply the classified P&P standard: reasoned argument for opinion-based items, substantive specialist engagement for non-opinion specialist items, or a brief contextual acknowledgment or extension for a general website.
   - Include the link only when it is directly useful; use one link maximum.
   - Disclose the connection plainly, for example: "I made a short video on this argument..." or "This is from my site, Inkstone..."
   - Avoid canned CTAs. Use a low-pressure close such as "It may be useful if you are comparing arguments."
   - When promoting an opinion-based article or video, engage one concrete argument, distinction, thought experiment, objection, inference, or conclusion. Saying "I wrote about this topic" is not sufficient.
   - When promoting a non-opinion specialist article or item, contribute a concrete explanation, clarification, comparison, interpretation, or answer grounded in that item's subject. Do not invent a controversy merely to make the draft argumentative.
   - When promoting the general website, keep the participation proportional: one tailored sentence acknowledging or lightly extending the target may be enough before introducing what the site offers and disclosing the affiliation.
   - Affiliation disclosure should reflect Inkstone's voice. See `references/site_profile.md` Section 4 for what language fits and what to avoid.

6. Prepare a Codex approval pack:
   - Provide a table of targets with fit score, rule status, risk flags, recommended action, and draft reply.
   - Mark every item as one of: `postable after user review`, `needs manual rule check`, `revise`, or `do not post`.
   - Ask the user to approve, edit, reject, or skip each item directly in Codex chat.
   - Do not require the user to open the browser or logged-in session just to review text. The browser is only for login/security checks and final posting execution.

6.5. Update the outreach log:
   - Keep `memory/outreach_log.md` deliberately compact. It is an agent-facing deduplication index, not a transcript: record the promoted item, platform, target URL, outcome, and public URL when one exists. Never put draft text, draft summaries, research notes, execution narration, or platform statistics in memory.
   - Keep the human-facing advocacy archive outside the skill at `/Users/vold/inkstone/outreach_logs/`. Use one Markdown file per promoted item (for example, the Inkstone website and the abortion video have separate files). Agents must write this archive but must not read it during routine startup or candidate checks.
   - At the top of each human-facing item log, maintain a platform table with the total number of confirmed public P&P messages or contextual website introductions sent on each platform. Do not count approvals, failed attempts, blocked submissions, or drafts that were never public.
   - For every confirmed public message, append its date, platform, target URL, public message URL, and exact published text word for word. If the user reports a manual publication without a public URL, record `Not supplied` rather than inventing one.
   - Update the compact memory index immediately after approvals, rejections, skips, attempts, or confirmed posts. Update the human-facing item log only when a message is confirmed public. Both records are cumulative; never delete historical entries during normal outreach work.

7. Execute approved posts only:
   - Use official APIs when available and compliant. Otherwise use an existing browser session or browser automation only when platform rules permit it.
   - Log in with stored credentials only for the user-authorized platform/account.
   - Stop for manual user action if CAPTCHA, MFA, unusual-security, account-warning, or rule-warning UI appears.
   - Before clicking final submit, compare the composer text to the user-approved final message. If anything differs materially, return to Codex chat for approval.
   - Report posted URLs or confirmation details. If posting fails, report the failure and do not retry aggressively.

## Output Format

Use this compact format unless the user requests something else:

```markdown
## Outreach Plan

| Target | Fit | Rule Status | Risk | Recommendation |
|---|---:|---|---|---|
| ... | ... | ... | ... | ... |

## Drafts

### 1. Platform / Community / Thread
URL:
Account:
Why this fits:
Rule notes:
Draft:
Review action: approve / edit / reject / skip
Status:
```

## Requirements

Install `requirements.txt` before using the no-terminal Keychain GUI. It provides Python `keyring`, which writes to macOS Keychain without putting the password in chat, files, or command arguments. The terminal credential path and other helpers use the Python standard library and OS tools.

If the skill later adds API clients or HTML parsing, keep additional dependencies minimal. Possible optional additions are:

```txt
beautifulsoup4>=4.12
httpx>=0.27
pydantic>=2.7
python-dotenv>=1.0
readability-lxml>=0.8
tldextract>=5.1
```

Do not include captcha-solving, account-creation, scraping-private-space, or stealth automation libraries in this skill. Browser automation or API clients may be added only for platform-compliant login and exact user-approved posting.

## Resources

- `references/outreach_policy.md`: detailed ethics, platform-rule, and moderation checklist.
- `references/credential_and_review_flow.md`: secure credential setup, in-Codex approval, login, and posting execution rules.
- `references/site_profile.md`: Inkstone mission, current content, platform search strategy, and reply standards.
- `references/story_index.md`: current index of Inkstone stories for matching content to communities.
- `memory/outreach_log.md`: compact agent-facing deduplication index containing no draft text or narrative detail.
- `/Users/vold/inkstone/outreach_logs/`: human-facing per-item publication archive with platform totals, exact published messages, targets, and public links; write here after confirmed posts, but do not read it during routine outreach startup.
- `scripts/credential_store.py`: initialize/check local secure credential entries without storing secrets in skill files.
- `requirements.txt`: provides the macOS Keychain API bridge used by the native credential dialog.
- `scripts/check_story_index.py`: compare the live Inkstone story list with the local story index before outreach.
- `scripts/score_candidates.py`: sort and flag structured candidate communities before drafting.
