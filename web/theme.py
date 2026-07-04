"""Palettes ported from gui.py's dark/light themes, applied via CSS variables.

Quasar toggles body.body--dark / body.body--light, so both palettes ship in
one stylesheet and the theme switch is instant.
"""

ACCENT = "#e07640"   # coral — same in both themes (light uses a deeper shade)

CSS = """
body.body--dark {
    --jda-bg: #0f1117; --jda-surface: #181b26; --jda-surface2: #1e2233;
    --jda-input: #0b0d16; --jda-border: #2a2e42;
    --jda-text: #eceef5; --jda-dim: #868fa8; --jda-muted: #4e5268;
    --jda-accent: #e07640;
}
body.body--light {
    --jda-bg: #f4f5f7; --jda-surface: #ffffff; --jda-surface2: #eaecf0;
    --jda-input: #ffffff; --jda-border: #d8dae4;
    --jda-text: #1a1c26; --jda-dim: #505468; --jda-muted: #8890a8;
    --jda-accent: #c0582a;
}
body { background: var(--jda-bg) !important; color: var(--jda-text); }

header.q-header {
    background: var(--jda-surface) !important;
    border-bottom: 1px solid var(--jda-border);
    color: var(--jda-text) !important;
}
aside.q-drawer {
    background: var(--jda-surface) !important;
    border-right: 1px solid var(--jda-border);
}

.jda-card {
    background: var(--jda-surface);
    border: 1px solid var(--jda-border);
    border-radius: 8px;
}
.jda-label { color: var(--jda-muted); letter-spacing: 0.08em; }
.jda-input .q-field__control { background: var(--jda-input); }
.jda-fill textarea { resize: none; line-height: 1.5; }
.jda-fill-lg textarea { height: calc(100vh - 330px) !important; }
.jda-fill-md textarea { height: calc(100vh - 480px) !important; min-height: 140px; }

.jda-output {
    height: calc(100vh - 225px);
    overflow-y: auto;
    padding: 16px 20px;
}
/* Tame markdown typography — headings barely larger than body text */
.jda-output h1, .jda-output h2, .jda-output h3, .jda-output h4 {
    font-size: 1rem;
    font-weight: 700;
    color: var(--jda-accent);
    margin: 1.1em 0 0.35em;
    line-height: 1.3;
}
.jda-output h1:first-child, .jda-output h2:first-child { margin-top: 0; }
.jda-output p, .jda-output li {
    font-size: 0.895rem;
    line-height: 1.6;
    margin: 0.35em 0;
}
.jda-output ul, .jda-output ol { padding-left: 1.2em; margin: 0.3em 0; }
.jda-output hr { border-color: var(--jda-border); margin: 0.9em 0; }
.jda-output strong { color: var(--jda-text); }

.jda-nav-active { color: var(--jda-accent) !important; }
"""
