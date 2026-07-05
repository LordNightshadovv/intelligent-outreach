# Credential And Review Flow

Use this reference before any credential setup, login, approval collection, or approved posting.

## Secret Storage

Use a real local secret store. Do not build or use plaintext credential files.

Preferred backends:

- macOS Keychain, via `scripts/credential_store.py`.
- A user-installed password manager CLI such as 1Password `op`, Bitwarden `bw`, or `pass`, if the user already uses it.
- Existing authenticated browser profiles, when the user intentionally authorizes that session.

Do not store credentials in:

- `SKILL.md`, reference files, scripts, or generated plans.
- `.env`, JSON, YAML, CSV, SQLite, shell scripts, browser screenshots, or terminal logs.
- Git-tracked files or files inside the project unless the file contains no secrets.

## Setup Sequence

1. Run `scripts/credential_store.py status`.
2. Prefer the no-terminal GUI path. Run `scripts/credential_store.py set-gui <platform>` and request permission to launch the macOS dialog. The dialog asks for the username and a hidden password, writes the credential directly to Keychain through the native keyring backend, and returns only success or cancellation to Codex.
3. If the username is already known and the user permits it, run `scripts/credential_store.py set-gui <platform> --username <username>` so the user sees only the hidden-password dialog.
4. Use `scripts/credential_store.py set <platform> --username <username>` only as a terminal fallback. macOS Keychain prompts directly for the password with terminal echo disabled.
5. If the platform needs a separate API token or app password, store it under a separate label such as `<platform>-api`.
6. If no supported secure backend exists, stop and ask the user to install or configure one.
7. Never ask the user to paste a password into Codex chat.

The GUI helper temporarily receives the secret inside its local process solely to call the macOS Keychain API. It never prints the secret, returns it to the agent, writes it to a file, or places it in a command argument.

## Login Execution

Use credentials only for the platform/account the user authorized. Prefer official APIs where they exist and permit the task.

When browser login is needed:

- Open the login page in the controlled browser.
- Prefer an already authenticated browser profile or native browser password autofill, because the agent never needs to retrieve the password.
- If a credential-aware browser adapter is available, fill credentials inside that adapter without printing secrets into chat or logs. The adapter may import `get_credential_for_automation(platform_name)` from `scripts/credential_store.py`, but it must not return the credential to the model or add a CLI command that prints passwords.
- If only a generic browser-control tool is available and no sealed credential adapter or native autofill exists, ask the user to complete login manually. Do not retrieve a password and relay it through Codex tool output.
- Stop if CAPTCHA, MFA, suspicious-login, email verification, phone verification, account-warning, or rule-warning UI appears.
- Ask the user to complete the security step manually in the browser.
- Continue only after the user confirms the account is logged in and the platform allows the intended action.

## In-Codex Approval

The user should be able to approve, edit, reject, or skip without opening the browser.

Present approvals in Codex chat using this shape:

```markdown
### Approval Item 1
Target:
Account:
Rule status:
Risk:
Final draft:

Reply with one of:
- approve 1
- edit 1: <replacement text>
- reject 1
- skip 1
```

Rules:

- Treat silence or ambiguous approval as no approval.
- Accept edits only from the user, then restate the final edited draft before posting.
- If the user approves multiple items, post only those exact items.
- Do not transform an approved draft after approval except for platform-required formatting such as preserving line breaks.
- If the target thread changes, new warnings appear, or the composer text differs materially, return to Codex chat for approval again.

## Posting Execution

For each approved item:

1. Recheck the target URL and visible rules.
2. Confirm the approved account is logged in.
3. Paste the approved final draft into the composer.
4. Compare the composer text with the approved draft.
5. Submit only when the text matches and no warnings/security checks appear.
6. Capture the posted URL or visible confirmation.
7. Report success, failure, or manual action needed in Codex chat.

Do not perform high-volume posting. Prefer a small number of high-fit replies.
