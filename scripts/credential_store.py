#!/usr/bin/env python3
"""Create and manage local secret entries for outreach accounts.

This helper intentionally does not provide a "print password" command. Login
automation should retrieve secrets inside the automation process and avoid
printing them into chat, terminal logs, or artifacts.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import sys


SERVICE_PREFIX = "codex-intelligent-outreach"

GUI_PROMPT_SCRIPT = r'''
on run argv
    set platformName to item 1 of argv
    set suppliedUsername to item 2 of argv

    if suppliedUsername is "" then
        set usernameDialog to display dialog "Enter the username or email for " & platformName & ":" default answer "" with title "Inkstone Outreach Account" buttons {"Cancel", "Continue"} default button "Continue" cancel button "Cancel"
        set accountName to text returned of usernameDialog
    else
        set accountName to suppliedUsername
    end if

    set passwordDialog to display dialog "Enter the password for " & platformName & ". It will be stored directly in macOS Keychain and will not be shown in Codex chat." default answer "" with hidden answer with title "Inkstone Outreach Password" buttons {"Cancel", "Save to Keychain"} default button "Save to Keychain" cancel button "Cancel"
    set accountPassword to text returned of passwordDialog
    return accountName & linefeed & accountPassword
end run
'''


def is_macos_keychain_available() -> bool:
    return platform.system() == "Darwin" and shutil.which("security") is not None


def is_gui_storage_available() -> bool:
    if platform.system() != "Darwin" or shutil.which("osascript") is None:
        return False
    try:
        import keyring
    except ImportError:
        return False
    backend = keyring.get_keyring()
    backend_name = f"{type(backend).__module__}.{type(backend).__name__}"
    return backend_name.startswith("keyring.backends.macOS.")


def service_name(platform_name: str) -> str:
    cleaned = platform_name.strip().lower().replace(" ", "-")
    if not cleaned:
        raise ValueError("Platform/account name cannot be empty.")
    return f"{SERVICE_PREFIX}:{cleaned}"


def run_security(args: list[str], input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["security", *args],
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def keychain_set(platform_name: str, username: str) -> None:
    service = service_name(platform_name)
    print(
        f"macOS Keychain will prompt for the password for {platform_name} ({username}).",
        file=sys.stderr,
    )
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-U",
            "-s",
            service,
            "-a",
            username,
            "-w",
        ],
        check=True,
    )
    print(json.dumps({"ok": True, "backend": "macos-keychain", "service": service, "username": username}))


def prompt_gui_credential(platform_name: str, username: str = "") -> tuple[str, str] | None:
    result = subprocess.run(
        ["osascript", "-e", GUI_PROMPT_SCRIPT, platform_name, username],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        if "User canceled" in result.stderr or "(-128)" in result.stderr:
            return None
        raise RuntimeError("macOS credential dialog failed to open.")

    account_name, separator, password = result.stdout.rstrip("\n").partition("\n")
    if not separator or not account_name or not password:
        raise ValueError("Username and password are required.")
    return account_name, password


def store_password_with_keyring(service: str, username: str, password: str) -> None:
    try:
        import keyring
    except ImportError as exc:
        raise RuntimeError("GUI storage requires the 'keyring' package.") from exc

    backend = keyring.get_keyring()
    backend_name = f"{type(backend).__module__}.{type(backend).__name__}"
    if not backend_name.startswith("keyring.backends.macOS."):
        raise RuntimeError(f"Expected macOS Keychain backend, found {backend_name}.")
    keyring.set_password(service, username, password)


def keychain_set_gui(platform_name: str, username: str = "") -> int:
    credential = prompt_gui_credential(platform_name, username)
    if credential is None:
        print(json.dumps({"ok": False, "cancelled": True, "platform": platform_name}))
        return 3

    account_name, password = credential
    service = service_name(platform_name)
    try:
        store_password_with_keyring(service, account_name, password)
    finally:
        password = ""
    print(json.dumps({"ok": True, "backend": "macos-keychain", "service": service}))
    return 0


def keychain_check(platform_name: str) -> int:
    service = service_name(platform_name)
    result = run_security(["find-generic-password", "-s", service], check=False)
    exists = result.returncode == 0
    print(json.dumps({"backend": "macos-keychain", "service": service, "exists": exists}))
    return 0 if exists else 1


def get_credential_for_automation(platform_name: str) -> dict[str, str]:
    """Return a credential for an automation script that imports this module.

    Do not expose this as a CLI command. Callers must avoid printing the returned
    password into chat, logs, screenshots, or artifacts.
    """
    if not is_macos_keychain_available():
        raise RuntimeError("No supported secure local credential backend found.")

    service = service_name(platform_name)
    password_result = run_security(["find-generic-password", "-s", service, "-w"])
    metadata_result = run_security(["find-generic-password", "-s", service], check=False)
    metadata = metadata_result.stdout + "\n" + metadata_result.stderr
    account_match = re.search(r'"acct"<blob>="([^"]*)"', metadata)
    username = account_match.group(1) if account_match else ""

    return {
        "backend": "macos-keychain",
        "service": service,
        "username": username,
        "password": password_result.stdout.rstrip("\n"),
    }


def keychain_delete(platform_name: str) -> None:
    service = service_name(platform_name)
    result = run_security(["delete-generic-password", "-s", service], check=False)
    if result.returncode == 0:
        print(json.dumps({"ok": True, "backend": "macos-keychain", "service": service, "deleted": True}))
        return
    print(json.dumps({"ok": True, "backend": "macos-keychain", "service": service, "deleted": False}))


def status() -> int:
    payload = {
        "supported": is_macos_keychain_available(),
        "backend": "macos-keychain" if is_macos_keychain_available() else None,
        "gui_storage_supported": is_gui_storage_available(),
        "stores_plaintext": False,
        "notes": "Prefer set-gui. Use set only as a terminal fallback. Do not print passwords into chat or logs.",
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["supported"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage secure local credential entries for intelligent outreach.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show whether a supported secure backend is available.")

    set_parser = subparsers.add_parser("set", help="Create or update a credential entry.")
    set_parser.add_argument("platform", help="Platform/account label, e.g. reddit-main.")
    set_parser.add_argument("--username", required=True, help="Username or email for the account.")

    gui_parser = subparsers.add_parser("set-gui", help="Store credentials through native macOS dialogs.")
    gui_parser.add_argument("platform", help="Platform/account label, e.g. reddit-main.")
    gui_parser.add_argument("--username", default="", help="Optional username; omit to enter it in the dialog.")

    check_parser = subparsers.add_parser("check", help="Check whether a credential entry exists.")
    check_parser.add_argument("platform", help="Platform/account label.")

    delete_parser = subparsers.add_parser("delete", help="Delete a credential entry.")
    delete_parser.add_argument("platform", help="Platform/account label.")

    args = parser.parse_args()

    if args.command == "status":
        return status()

    if not is_macos_keychain_available():
        print("No supported secure local credential backend found.", file=sys.stderr)
        return 2

    if args.command == "set":
        keychain_set(args.platform, args.username)
        return 0
    if args.command == "set-gui":
        return keychain_set_gui(args.platform, args.username)
    if args.command == "check":
        return keychain_check(args.platform)
    if args.command == "delete":
        keychain_delete(args.platform)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
