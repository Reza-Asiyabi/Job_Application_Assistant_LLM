"""
Web GUI (NiceGUI) — incremental migration off tkinter.

Run:  python web_gui.py     then open http://localhost:8080
      http://localhost:8080/?demo=1 renders sample output for styling checks.

Pages so far: Evaluate, Generate (CV summary / cover letter / LinkedIn), Q&A.
The tkinter GUI (launch.py) remains fully functional until parity.
"""
from web.main import run_app

if __name__ in {"__main__", "__mp_main__"}:
    run_app(show=False)
