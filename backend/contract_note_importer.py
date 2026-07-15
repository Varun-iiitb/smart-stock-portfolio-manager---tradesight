"""
Contract Note Importer
Parses StockHolding Services CCN PDF files and inserts BUY trades into stock.db.
Also runs a background watcher thread that picks up new CCN files automatically.
"""

import os
import re
import sqlite3
import time
import threading
import requests
from datetime import datetime

CONTRACT_NOTES_FOLDER = r"C:\Users\anura\Desktop\contract notes"
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FILES_DB = os.path.join(_SCRIPT_DIR, "processed_files.db")
STOCK_DB = os.path.join(_SCRIPT_DIR, "stock.db")


# ── Processed-files tracking ────────────────────────────────────────────────

def _init_processed_db():
    conn = sqlite3.connect(PROCESSED_FILES_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ProcessedFiles (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            filename          TEXT NOT NULL UNIQUE,
            contract_note_no  TEXT,
            processed_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            username          TEXT,
            trades_imported   INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def _is_processed(filename, contract_note_no=None):
    """Return True if this file OR its contract note number was already imported."""
    _init_processed_db()
    conn = sqlite3.connect(PROCESSED_FILES_DB)
    by_file = conn.execute("SELECT id FROM ProcessedFiles WHERE filename=?", (filename,)).fetchone()
    if by_file:
        conn.close()
        return True
    if contract_note_no:
        by_cn = conn.execute(
            "SELECT id FROM ProcessedFiles WHERE contract_note_no=?", (contract_note_no,)
        ).fetchone()
        if by_cn:
            conn.close()
            return True
    conn.close()
    return False


def _mark_processed(filename, username, count, contract_note_no=None):
    conn = sqlite3.connect(PROCESSED_FILES_DB)
    conn.execute(
        "INSERT OR REPLACE INTO ProcessedFiles (filename, contract_note_no, username, trades_imported)"
        " VALUES (?,?,?,?)",
        (filename, contract_note_no, username, count)
    )
    conn.commit()
    conn.close()


def get_processed_files():
    """Return list of dicts describing every processed file."""
    _init_processed_db()
    conn = sqlite3.connect(PROCESSED_FILES_DB)
    rows = conn.execute(
        "SELECT filename, processed_at, trades_imported, contract_note_no"
        " FROM ProcessedFiles ORDER BY processed_at DESC"
    ).fetchall()
    conn.close()
    return [
        {"filename": r[0], "processed_at": r[1], "trades_imported": r[2], "contract_note_no": r[3]}
        for r in rows
    ]


# ── Ticker resolution ────────────────────────────────────────────────────────

def _resolve_ticker(isin, company_name):
    """
    Find the Yahoo Finance ticker for an Indian stock.
    Tries ISIN first, then 'COMPANY NSE', then bare company name.
    Strongly prefers .NS (NSE) symbols; falls back to .BO (BSE) or any result.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    url = "https://query2.finance.yahoo.com/v1/finance/search"

    queries = [isin, company_name + " NSE", company_name]
    for q in queries:
        try:
            resp = requests.get(url, headers=headers,
                                params={"q": q, "quotesCount": 8, "newsCount": 0},
                                timeout=6)
            if resp.status_code != 200:
                continue
            quotes = resp.json().get("quotes", [])
            for sym_suffix in (".NS", ".BO"):
                for qt in quotes:
                    sym = qt.get("symbol", "")
                    if sym.endswith(sym_suffix):
                        return sym
            if quotes:
                return quotes[0].get("symbol")
        except Exception as exc:
            print(f"[importer] ticker search error ({q}): {exc}")
    return None


# ── Date parsing ─────────────────────────────────────────────────────────────

def _parse_date(raw):
    """Convert '25-Jul-25' / '25-Jul-2025' / '25-07-2025' to 'YYYY-MM-DD'."""
    raw = raw.strip()
    for fmt in ("%d-%b-%y", "%d-%b-%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return datetime.today().strftime("%Y-%m-%d")


# ── PDF parser ───────────────────────────────────────────────────────────────

def _parse_pdf(pdf_path):
    """
    Parse a StockHolding Services CCN contract-note PDF.
    Returns (contract_note_no: str|None, trades: list of dicts)
    Each trade dict: {isin, company_name, action, quantity, price, trade_date}
    """
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # Extract contract note number (used for dedup across duplicate PDFs)
    contract_note_no = None
    cn_m = re.search(r"Contract\s+Note\s+No\.?\s*(\S+)", full_text, re.IGNORECASE)
    if cn_m:
        contract_note_no = cn_m.group(1).strip()

    # Extract trade date from header
    trade_date = datetime.today().strftime("%Y-%m-%d")
    m = re.search(r"Trade\s+Date\s+(\d{1,2}[-/][A-Za-z0-9]+[-/]\d{2,4})", full_text, re.IGNORECASE)
    if m:
        trade_date = _parse_date(m.group(1))

    trades = []

    # ── Strategy 1: Annexure-A detail lines ─────────────────────────────────
    # Format:
    # {order_no} {HH:MM:SS} {trade_no} {HH:MM:SS} {COMPANY}-Cash-{ISIN} {B|S} {qty} {price} ...
    annexure_re = re.compile(
        r"\d{10,}\s+\d{2}:\d{2}:\d{2}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+"
        r"([A-Z][A-Z0-9\s&./()'-]+?)-Cash-(IN[A-Z0-9]{10})\s+([BS])\s+(\d+)\s+([\d.]+)",
        re.MULTILINE,
    )
    for m in annexure_re.finditer(full_text):
        trades.append({
            "company_name": m.group(1).strip(),
            "isin":         m.group(2),
            "action":       m.group(3),
            "quantity":     int(m.group(4)),
            "price":        float(m.group(5)),
            "trade_date":   trade_date,
        })

    if trades:
        # Deduplicate: same ISIN + quantity + price can appear in multiple settlement sections
        seen = set()
        unique = []
        for t in trades:
            key = (t["isin"], t["action"], t["quantity"], t["price"])
            if key not in seen:
                seen.add(key)
                unique.append(t)
        return contract_note_no, unique

    # ── Strategy 2: Main equity table rows ──────────────────────────────────
    # ISIN line:  INE036D01028 KARUR VYSYA BANK LTD/KARURVYSYAEQ
    # Data line:  20 260.400000 ...
    equity_re = re.compile(
        r"(IN[A-Z0-9]{10})\s+([A-Z][A-Z0-9\s&./()'-]+?)(?:/\S+)?\n"
        r"(\d+)\s+([\d.]+)",
        re.MULTILINE,
    )
    for m in equity_re.finditer(full_text):
        trades.append({
            "company_name": m.group(2).strip(),
            "isin":         m.group(1),
            "action":       "B",
            "quantity":     int(m.group(3)),
            "price":        float(m.group(4)),
            "trade_date":   trade_date,
        })

    return contract_note_no, trades


# ── Single-file importer ─────────────────────────────────────────────────────

def import_contract_note(pdf_path, username):
    """
    Parse one CCN PDF and insert BUY trades into stock.db for the given user.
    Skips the file if its contract note number was already processed (duplicate PDF).
    Returns (success: bool, message: str, imported_count: int)
    """
    filename = os.path.basename(pdf_path)

    try:
        contract_note_no, trades = _parse_pdf(pdf_path)
    except Exception as exc:
        return False, f"{filename}: parse error — {exc}", 0

    # Skip duplicate PDFs (same contract note number, different filename)
    if contract_note_no and _is_processed(filename, contract_note_no):
        _mark_processed(filename, username, 0, contract_note_no)
        return True, f"{filename}: duplicate of CN#{contract_note_no} (skipped)", 0

    if not trades:
        _mark_processed(filename, username, 0, contract_note_no)
        return True, f"{filename}: no trades found in PDF", 0

    imported = 0
    skipped  = []

    conn = sqlite3.connect(STOCK_DB)
    try:
        cur = conn.cursor()
        for t in trades:
            if t["action"] != "B":
                continue
            ticker = _resolve_ticker(t["isin"], t["company_name"])
            if not ticker:
                skipped.append(f"{t['company_name']} ({t['isin']})")
                continue
            cur.execute(
                "INSERT INTO Stocks (Username, StockName, Quantity, Price_per_share, Date, ticker_symbol)"
                " VALUES (?,?,?,?,?,?)",
                (username, t["company_name"], t["quantity"], t["price"], t["trade_date"], ticker),
            )
            imported += 1
        conn.commit()
    finally:
        conn.close()

    _mark_processed(filename, username, imported, contract_note_no)

    msg = f"{filename}: imported {imported} trade(s)"
    if skipped:
        msg += " | could not resolve ticker for: " + ", ".join(skipped)
    return True, msg, imported


# ── Bulk scanner ─────────────────────────────────────────────────────────────

def scan_and_import_all(username, clear_existing=False):
    """
    Scan CONTRACT_NOTES_FOLDER for CCN*.pdf files and import all unprocessed ones.
    If clear_existing=True, wipe the user's portfolio and reset processed-file log first.
    Returns (results: list[str], total_imported: int)
    """
    _init_processed_db()

    if not os.path.isdir(CONTRACT_NOTES_FOLDER):
        return [f"Folder not found: {CONTRACT_NOTES_FOLDER}"], 0

    if clear_existing:
        conn = sqlite3.connect(STOCK_DB)
        conn.execute("DELETE FROM Stocks WHERE Username=?", (username,))
        conn.commit()
        conn.close()
        conn = sqlite3.connect(PROCESSED_FILES_DB)
        conn.execute("DELETE FROM ProcessedFiles")
        conn.commit()
        conn.close()

    files = sorted(
        f for f in os.listdir(CONTRACT_NOTES_FOLDER)
        if f.upper().startswith("CCN") and f.lower().endswith(".pdf")
    )

    results = []
    total   = 0

    for filename in files:
        if _is_processed(filename):
            results.append(f"{filename}: already imported (skipped)")
            continue
        path = os.path.join(CONTRACT_NOTES_FOLDER, filename)
        _, msg, cnt = import_contract_note(path, username)
        results.append(msg)
        total += cnt

    if not files:
        results.append("No CCN PDF files found in the contract notes folder.")

    return results, total


# ── Background file watcher ──────────────────────────────────────────────────

_watcher_username = None
_watcher_lock     = threading.Lock()


def set_watcher_username(username):
    global _watcher_username
    with _watcher_lock:
        _watcher_username = username


def _get_watcher_username():
    with _watcher_lock:
        return _watcher_username


class _Watcher(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="contract-note-watcher")
        self._known: set = set()

    def run(self):
        _init_processed_db()
        if os.path.isdir(CONTRACT_NOTES_FOLDER):
            self._known = {
                f for f in os.listdir(CONTRACT_NOTES_FOLDER)
                if f.upper().startswith("CCN") and f.lower().endswith(".pdf")
            }
        print(f"[watcher] monitoring: {CONTRACT_NOTES_FOLDER}")

        while True:
            time.sleep(10)
            try:
                if not os.path.isdir(CONTRACT_NOTES_FOLDER):
                    continue
                current = {
                    f for f in os.listdir(CONTRACT_NOTES_FOLDER)
                    if f.upper().startswith("CCN") and f.lower().endswith(".pdf")
                }
                new_files = current - self._known
                self._known = current

                username = _get_watcher_username()
                if not username:
                    continue

                for fname in sorted(new_files):
                    if _is_processed(fname, None):
                        continue
                    print(f"[watcher] new contract note detected: {fname}")
                    path = os.path.join(CONTRACT_NOTES_FOLDER, fname)
                    _, msg, _ = import_contract_note(path, username)
                    print(f"[watcher] {msg}")
            except Exception as exc:
                print(f"[watcher] error: {exc}")


_watcher = None  # type: _Watcher


def start_watcher():
    global _watcher
    if _watcher is None:
        _watcher = _Watcher()
        _watcher.start()
