"""
Gmail Contract-Note Fetcher
============================
Pulls SHCIL / StockHolding Services contract-note PDFs straight from Gmail
(sender: cnote@shcilservices.com) and drops them into the same folder that
``contract_note_importer`` watches — so a fresh trade e-mail becomes an imported
portfolio position with no manual downloading.

Ported from the standalone "email-agent" project, trimmed to the contract-note
slice only. Auth uses the same credentials.json / token.json (gmail.modify
scope), so the existing Gmail authorisation is reused with no re-login.

The heavy Google API imports are done lazily inside the functions so that a
missing dependency degrades *only* the Gmail feature instead of taking down the
whole Flask app at import time.
"""

import os
import json
import base64
import threading
import time

from contract_note_importer import CONTRACT_NOTES_FOLDER

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

_SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(_SCRIPT_DIR, "credentials.json")
TOKEN_FILE       = os.path.join(_SCRIPT_DIR, "token.json")
SEEN_IDS_FILE    = os.path.join(_SCRIPT_DIR, "gmail_seen_ids.json")

# Only e-mails from this sender are treated as contract notes.
CONTRACT_NOTE_SENDER = "cnote@shcilservices.com"

# How often the background poller checks Gmail (seconds).
POLL_INTERVAL = 300


# ── seen-message tracking ────────────────────────────────────────────────────

def _load_seen() -> set:
    if os.path.exists(SEEN_IDS_FILE):
        try:
            with open(SEEN_IDS_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def _save_seen(seen: set) -> None:
    try:
        with open(SEEN_IDS_FILE, "w") as f:
            json.dump(list(seen), f)
    except Exception as exc:
        print(f"[gmail] could not save seen-ids: {exc}")


# ── auth ─────────────────────────────────────────────────────────────────────

def _authenticate(interactive: bool = True):
    """Return valid Gmail credentials.

    Tries the saved token, then a silent refresh. If the token is dead and
    ``interactive`` is True, opens a browser for a one-time re-login; if False
    (the background poller), it raises instead of popping a browser, so re-auth
    only ever happens when the user explicitly asks for it."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    from google.auth.exceptions import RefreshError

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        refreshed = False
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                refreshed = True
            except RefreshError as exc:
                # Token expired/revoked (a "Testing"-mode app rotates its refresh
                # token every 7 days). Needs a fresh interactive authorisation.
                print(f"[gmail] token refresh failed: {exc}")
                creds = None

        if not refreshed:
            if not interactive:
                raise RuntimeError(
                    "Gmail authorisation expired. Click 'Import Contract Notes' "
                    "in the app to re-authorise (a browser window will open)."
                )
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Gmail credentials.json not found at {CREDENTIALS_FILE}. "
                    "Cannot fetch contract notes from e-mail."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def _build_service(interactive: bool = True):
    from googleapiclient.discovery import build
    return build("gmail", "v1", credentials=_authenticate(interactive=interactive))


# ── PDF download ─────────────────────────────────────────────────────────────

def _download_pdfs(service, msg_id: str) -> list:
    """Save every PDF attachment of one message into the contract-notes folder.
    Skips files that already exist (contract-note filenames are unique), so this
    is safe to run repeatedly without creating duplicates."""
    os.makedirs(CONTRACT_NOTES_FOLDER, exist_ok=True)
    saved = []

    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    parts = msg.get("payload", {}).get("parts", [])

    for part in parts:
        filename = part.get("filename", "")
        if not filename.lower().endswith(".pdf"):
            continue

        save_path = os.path.join(CONTRACT_NOTES_FOLDER, filename)
        if os.path.exists(save_path):
            continue  # already downloaded earlier (by us or the mail agent)

        body = part.get("body", {})
        attachment_id = body.get("attachmentId")
        data = body.get("data")
        if attachment_id:
            attachment = service.users().messages().attachments().get(
                userId="me", messageId=msg_id, id=attachment_id
            ).execute()
            data = attachment.get("data", "")
        if not data:
            continue

        with open(save_path, "wb") as f:
            f.write(base64.urlsafe_b64decode(data))
        saved.append(save_path)
        print(f"[gmail] saved contract note: {filename}")

    return saved


# ── public API ───────────────────────────────────────────────────────────────

def fetch_new_contract_notes(max_results: int = 50, interactive: bool = True) -> list:
    """Scan Gmail for contract-note e-mails and download any new PDFs into the
    contract-notes folder. Returns the list of newly saved file paths.

    ``interactive=True`` (the default, used by the manual Import button) allows a
    browser re-login if the token has expired; ``interactive=False`` (the
    background poller) raises instead of opening a browser."""
    service = _build_service(interactive=interactive)
    seen = _load_seen()

    query = f"from:{CONTRACT_NOTE_SENDER} has:attachment filename:pdf"
    resp = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    messages = resp.get("messages", [])

    downloaded = []
    for m in messages:
        mid = m["id"]
        if mid in seen:
            continue
        try:
            downloaded.extend(_download_pdfs(service, mid))
        except Exception as exc:
            print(f"[gmail] error downloading message {mid}: {exc}")
            continue
        seen.add(mid)

    _save_seen(seen)

    if downloaded:
        print(f"[gmail] fetched {len(downloaded)} new contract note(s).")
    return downloaded


# ── background poller ────────────────────────────────────────────────────────

_watcher = None
_watcher_lock = threading.Lock()


class _GmailWatcher(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="gmail-contract-note-fetcher")

    def run(self):
        print(f"[gmail] contract-note fetcher polling every {POLL_INTERVAL}s "
              f"(sender: {CONTRACT_NOTE_SENDER})")
        while True:
            try:
                # Background: never open a browser. If the token is dead, this
                # raises and we just wait — the user re-auths via the Import
                # button, after which the refreshed token makes polling work.
                fetch_new_contract_notes(interactive=False)
            except Exception as exc:
                print(f"[gmail] fetch error: {exc}")
            time.sleep(POLL_INTERVAL)


def start_gmail_watcher():
    """Start the background Gmail poller once. The downloaded PDFs are imported
    by contract_note_importer's folder-watcher (once a username is set)."""
    global _watcher
    with _watcher_lock:
        if _watcher is None:
            _watcher = _GmailWatcher()
            _watcher.start()


if __name__ == "__main__":
    new = fetch_new_contract_notes()
    print(f"Done. {len(new)} new file(s) downloaded to {CONTRACT_NOTES_FOLDER}.")
