"""Desktop launcher for Tradesight.

Starts the Flask app under the Waitress production server and opens it in an
app-style browser window. If the app is already running, it just opens a new
window instead of starting a second server.
"""
import os
import sys
import time
import socket
import threading
import subprocess
import webbrowser

# All relative paths in app.py (databases, static/) must resolve to this folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"


def server_is_up():
    """Return True if something is already listening on HOST:PORT."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, PORT)) == 0


def open_app_window():
    """Open the app in a clean app-style window (Edge app mode), or fall back
    to the default browser."""
    edge_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for exe in edge_candidates:
        if os.path.exists(exe):
            subprocess.Popen([exe, f"--app={URL}"])
            return
    webbrowser.open(URL)


def main():
    # Already running? Just open another window and exit.
    if server_is_up():
        open_app_window()
        return

    # Open the browser once the server has bound the port.
    def delayed_open():
        for _ in range(60):  # wait up to ~30s
            if server_is_up():
                break
            time.sleep(0.5)
        open_app_window()

    threading.Thread(target=delayed_open, daemon=True).start()

    from waitress import serve
    from app import app
    serve(app, host=HOST, port=PORT, threads=6)


if __name__ == "__main__":
    main()
