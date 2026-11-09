#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import json
import sys
import urllib.request
import urllib.error
import webbrowser
import time
import threading
import shutil
from datetime import datetime

GITHUB_API = "https://api.github.com"
CONFIG_FILE = os.path.expanduser("~/.config/gh-setup/config.json")
BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
SURFACE = "#313244"
MUTED = "#a6adc8"
CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")


def gen_readme(name, desc, username, license_name="MIT"):
    L = []
    L.append("# " + name)
    L.append("")
    L.append(desc or "A project.")
    L.append("")
    L.append("## Quick Start")
    L.append("")
    L.append("    git clone https://github.com/" + username + "/" + name + ".git")
    L.append("    cd " + name)
    L.append("")
    L.append("## Prerequisites")
    L.append("")
    L.append("- Linux")
    L.append("- Python 3.8+")
    L.append("- Git")
    L.append("")
    L.append("## License")
    L.append("")
    L.append(license_name + " License - see LICENSE")
    L.append("")
    L.append("## Contributing")
    L.append("")
    L.append("See CONTRIBUTING.md")
    L.append("")
    L.append("---")
    L.append("")
    L.append("Made on Linux")
    return "\n".join(L) + "\n"


def gen_license_mit(username, year):
    L = []
    L.append("MIT License")
    L.append("")
    L.append("Copyright (c) " + str(year) + " " + username)
    L.append("")
    L.append("Permission is hereby granted, free of charge, to any person obtaining a copy")
    L.append('of this software and associated documentation files (the "Software"), to deal')
    L.append("in the Software without restriction, including without limitation the rights")
    L.append("to use, copy, modify, merge, publish, distribute, sublicense, and/or sell")
    L.append("copies of the Software, and to permit persons to whom the Software is")
    L.append("furnished to do so, subject to the following conditions:")
    L.append("")
    L.append("The above copyright notice and this permission notice shall be included in all")
    L.append("copies or substantial portions of the Software.")
    L.append("")
    L.append('THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR')
    L.append("IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,")
    L.append("FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE")
    L.append("AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER")
    L.append("LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,")
    L.append("OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE")
    L.append("SOFTWARE.")
    return "\n".join(L) + "\n"


def gen_license_gpl(username, year):
    L = []
    L.append("GNU GENERAL PUBLIC LICENSE")
    L.append("Version 3, 29 June 2007")
    L.append("")
    L.append("Copyright (C) " + str(year) + " " + username)
    L.append("")
    L.append("This program is free software: you can redistribute it and/or modify")
    L.append("it under the terms of the GNU General Public License as published by")
    L.append("the Free Software Foundation, either version 3 of the License, or")
    L.append("(at your option) any later version.")
    L.append("")
    L.append("This program is distributed in the hope that it will be useful,")
    L.append("but WITHOUT ANY WARRANTY; without even the implied warranty of")
    L.append("MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
    L.append("GNU General Public License for more details.")
    L.append("")
    L.append("You should have received a copy of the GNU General Public License")
    L.append("along with this program.  If not, see <https://www.gnu.org/licenses/>.")
    return "\n".join(L) + "\n"


def gen_contributing(name):
    L = []
    L.append("# Contributing to " + name)
    L.append("")
    L.append("## How to Contribute")
    L.append("")
    L.append("1. Fork the repo")
    L.append("2. Create a branch: git checkout -b feature/my-feature")
    L.append("3. Commit: git commit -m 'Add feature'")
    L.append("4. Push: git push origin feature/my-feature")
    L.append("5. Open a Pull Request")
    L.append("")
    L.append("## Commit Messages")
    L.append("")
    L.append("- feat: new feature")
    L.append("- fix: bug fix")
    L.append("- docs: documentation only")
    L.append("- style: formatting")
    L.append("- refactor: code change")
    L.append("- perf: performance")
    L.append("- test: adding tests")
    L.append("- chore: build/deps")
    return "\n".join(L) + "\n"


def gen_changelog():
    L = []
    L.append("# Changelog")
    L.append("")
    L.append("All notable changes are documented here.")
    L.append("Based on Keep a Changelog + Semantic Versioning.")
    L.append("")
    L.append("## [Unreleased]")
    L.append("")
    L.append("### Added")
    L.append("- Initial release")
    return "\n".join(L) + "\n"


def gen_gitignore():
    L = []
    L.append("# Python")
    L.append("__pycache__/")
    L.append("*.py[cod]")
    L.append("*.so")
    L.append("build/")
    L.append("dist/")
    L.append("*.egg-info/")
    L.append("")
    L.append("# Virtual env")
    L.append("venv/")
    L.append(".venv/")
    L.append("")
    L.append("# IDE")
    L.append(".vscode/")
    L.append(".idea/")
    L.append("*.swp")
    L.append("")
    L.append("# OS")
    L.append(".DS_Store")
    L.append("Thumbs.db")
    L.append("")
    L.append("# Env")
    L.append(".env")
    L.append("*.log")
    L.append("")
    L.append("# Media")
    L.append("*.mp4")
    L.append("*.mkv")
    L.append("*.avi")
    return "\n".join(L) + "\n"


def gen_gitattributes():
    L = []
    L.append("* text=auto")
    L.append("*.py  text diff=python")
    L.append("*.sh  text")
    L.append("*.md  text")
    L.append("*.json text")
    L.append("*.yml text")
    L.append("*.png binary")
    L.append("*.jpg binary")
    L.append("*.glsl text")
    return "\n".join(L) + "\n"


def gen_editorconfig():
    L = []
    L.append("root = true")
    L.append("")
    L.append("[*]")
    L.append("charset = utf-8")
    L.append("end_of_line = lf")
    L.append("insert_final_newline = true")
    L.append("trim_trailing_whitespace = true")
    L.append("indent_style = space")
    L.append("indent_size = 4")
    L.append("")
    L.append("[*.md]")
    L.append("trim_trailing_whitespace = false")
    return "\n".join(L) + "\n"


def gen_notes(name):
    L = []
    L.append("# " + name + " - Developer Notes")
    L.append("")
    L.append("## Setup")
    L.append("")
    L.append("    git clone https://github.com/YOUR_USER/" + name + ".git")
    L.append("    cd " + name)
    L.append("    chmod +x *.sh *.py")
    L.append("")
    L.append("## Running")
    L.append("")
    L.append("    python3 main.py")
    L.append("")
    L.append("## TODO")
    L.append("")
    L.append("- [ ] Add tests")
    L.append("- [ ] CI/CD")
    L.append("- [ ] Packaging")
    return "\n".join(L) + "\n"


def gen_issue_template():
    L = []
    L.append("## Bug Report")
    L.append("")
    L.append("**Describe the bug**")
    L.append("")
    L.append("**To Reproduce**")
    L.append("1. Go to...")
    L.append("2. Click...")
    L.append("3. See error")
    L.append("")
    L.append("**Expected behavior**")
    L.append("")
    L.append("**Environment**")
    L.append("- OS:")
    L.append("- Version:")
    L.append("- GPU:")
    return "\n".join(L) + "\n"


def gen_pr_template():
    L = []
    L.append("## Description")
    L.append("")
    L.append("What does this PR do?")
    L.append("")
    L.append("## Type")
    L.append("")
    L.append("- [ ] Bug fix")
    L.append("- [ ] New feature")
    L.append("- [ ] Documentation")
    L.append("- [ ] Refactoring")
    L.append("")
    L.append("## Checklist")
    L.append("")
    L.append("- [ ] Self-reviewed")
    L.append("- [ ] Tests updated")
    L.append("- [ ] Docs updated")
    return "\n".join(L) + "\n"


def gen_cicd(name):
    L = []
    L.append("name: CI")
    L.append("")
    L.append("on:")
    L.append("  push:")
    L.append("    branches: [main]")
    L.append("  pull_request:")
    L.append("    branches: [main]")
    L.append("")
    L.append("jobs:")
    L.append("  test:")
    L.append("    runs-on: ubuntu-latest")
    L.append("    steps:")
    L.append("      - uses: actions/checkout@v4")
    L.append("      - name: Set up Python")
    L.append("        uses: actions/setup-python@v5")
    L.append("        with:")
    L.append("          python-version: '3.11'")
    L.append("      - name: Lint")
    L.append("        run: python -m py_compile $(git ls-files '*.py') 2>/dev/null || true")
    return "\n".join(L) + "\n"


class GitHub:
    def __init__(self, token):
        self.token = token
        self.user = None

    def _req(self, method, path, data=None):
        url = GITHUB_API + path
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "gh-setup"}
        if self.token:
            headers["Authorization"] = "token " + self.token
        body = None
        if data:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
        r = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(r) as resp:
                if resp.status == 204:
                    return None
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            try:
                raise Exception(json.loads(err).get("message", err))
            except:
                raise Exception("HTTP " + str(e.code))

    def get_user(self):
        self.user = self._req("GET", "/user")
        return self.user

    def create_repo(self, name, desc, private):
        return self._req("POST", "/user/repos", {"name": name, "description": desc, "private": private})

    def repo_exists(self, name):
        try:
            self._req("GET", "/repos/" + self.user["login"] + "/" + name)
            return True
        except:
            return False


class DeviceFlow:
    def __init__(self, client_id):
        self.client_id = client_id
        self.device_code = None
        self.user_code = None
        self.uri = None
        self.interval = 5
        self.expiry = 900

    def start(self):
        data = json.dumps({"client_id": self.client_id, "scope": "repo"}).encode()
        r = urllib.request.Request(GITHUB_API + "/login/device/code", data=data,
                                   headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(r) as resp:
            j = json.loads(resp.read().decode())
            self.device_code = j["device_code"]
            self.user_code = j["user_code"]
            self.uri = j["verification_uri"]
            self.interval = j.get("interval", 5)
            self.expiry = j.get("expires_in", 900)

    def poll(self):
        data = json.dumps({"client_id": self.client_id, "device_code": self.device_code}).encode()
        r = urllib.request.Request(GITHUB_API + "/login/oauth/access_token", data=data,
                                   headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())


def git_available():
    return shutil.which("git") is not None

def git_run(cwd, *args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=cwd)

def is_git_repo(p):
    return os.path.exists(os.path.join(p, ".git"))

def get_remote_url(p):
    r = git_run(p, "remote", "get-url", "origin")
    return r.stdout.strip() if r.returncode == 0 else None

def get_status(p):
    r = git_run(p, "status", "--porcelain")
    return [l for l in r.stdout.strip().split("\n") if l]

def get_branch(p):
    r = git_run(p, "rev-parse", "--abbrev-ref", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else "main"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


class GHSetup:
    def __init__(self, root):
        self.root = root
        root.title("GitHub Repo Setup & Sync")
        root.geometry("700x900")
        root.resizable(False, False)
        root.configure(bg=BG)
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("TFrame", background=BG)
        st.configure("TLabel", background=BG, foreground=FG, font=("Arial", 10))
        st.configure("Title.TLabel", background=BG, foreground=FG, font=("Arial", 14, "bold"))
        st.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Arial", 9))
        st.configure("Section.TLabel", background=BG, foreground=ACCENT, font=("Arial", 10, "bold"))
        st.configure("TEntry", fieldbackground=SURFACE, foreground=FG, font=("Arial", 10))
        st.configure("TCheckbutton", background=BG, foreground=FG, font=("Arial", 9))
        st.configure("TRadiobutton", background=BG, foreground=FG, font=("Arial", 9))
        st.configure("Status.TLabel", background=BG, foreground=GREEN, font=("Arial", 9))
        self.cfg = load_config()
        self.gh = None
        self.local_path = self.cfg.get("local_path", "")
        self.repo_name = self.cfg.get("repo_name", "")
        self.existing = self.local_path and is_git_repo(self.local_path)
        self.sv = {
            "readme": tk.BooleanVar(value=True),
            "license": tk.BooleanVar(value=True),
            "contributing": tk.BooleanVar(value=True),
            "changelog": tk.BooleanVar(value=True),
            "gitignore": tk.BooleanVar(value=True),
            "gitattributes": tk.BooleanVar(value=True),
            "editorconfig": tk.BooleanVar(value=True),
            "notes": tk.BooleanVar(value=True),
            "issue": tk.BooleanVar(value=True),
            "pr": tk.BooleanVar(value=True),
            "cicd": tk.BooleanVar(value=False),
        }
        self.build_ui()

    def build_ui(self):
        ttk.Label(self.root, text="GitHub Repo Setup & Sync", style="Title.TLabel").pack(anchor=tk.W, padx=15, pady=(12, 2))
        ttk.Label(self.root, text="Create + scaffold first run | Sync subsequent runs", style="Sub.TLabel").pack(anchor=tk.W, padx=15)
        mid = ttk.Frame(self.root)
        mid.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        canvas = tk.Canvas(mid, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=canvas.yview)
        self.inner = ttk.Frame(canvas)
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        self.build_sections()
        btn = ttk.Frame(self.root)
        btn.pack(fill=tk.X, padx=15, pady=(8, 5))
        if self.existing:
            tk.Button(btn, text="  PUSH  ", command=self.do_push, bg=GREEN, fg=BG, relief=tk.RAISED, bd=2, font=("Arial", 11, "bold"), padx=15, pady=7, cursor="hand2").pack(side=tk.LEFT, padx=(0, 6))
            tk.Button(btn, text="  PULL  ", command=self.do_pull, bg=ACCENT, fg=BG, relief=tk.RAISED, bd=2, font=("Arial", 11, "bold"), padx=15, pady=7, cursor="hand2").pack(side=tk.LEFT, padx=3)
            tk.Button(btn, text="  SYNC  ", command=self.do_sync, bg=YELLOW, fg=BG, relief=tk.RAISED, bd=2, font=("Arial", 11, "bold"), padx=15, pady=7, cursor="hand2").pack(side=tk.LEFT, padx=3)
        else:
            tk.Button(btn, text="  CREATE + SCAFFOLD + PUSH  ", command=self.do_create, bg=GREEN, fg=BG, relief=tk.RAISED, bd=2, font=("Arial", 11, "bold"), padx=15, pady=7, cursor="hand2").pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn, text="  RESET  ", command=self.do_reset, bg=RED, fg=BG, relief=tk.RAISED, bd=2, font=("Arial", 10, "bold"), padx=10, pady=7, cursor="hand2").pack(side=tk.RIGHT, padx=(6, 0))
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status, style="Status.TLabel").pack(fill=tk.X, padx=15, pady=(0, 8))

    def build_sections(self):
        self.sec("AUTHENTICATION")
        af = ttk.Frame(self.inner); af.pack(fill=tk.X, pady=2)
        self.auth_method = tk.StringVar(value="browser" if CLIENT_ID else "token")
        ttk.Radiobutton(af, text="Browser", value="browser", variable=self.auth_method).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(af, text="Token", value="token", variable=self.auth_method).pack(side=tk.LEFT)
        if CLIENT_ID:
            tk.Button(af, text="Login via Browser", command=self.do_browser_auth, bg=ACCENT, fg=BG, relief=tk.RAISED, bd=2, font=("Arial", 9, "bold"), padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=(15, 0))
        tr = ttk.Frame(self.inner); tr.pack(fill=tk.X, pady=2)
        ttk.Label(tr, text="  Token: ").pack(side=tk.LEFT)
        self.token_var = tk.StringVar(value=self.cfg.get("token", ""))
        tk.Entry(tr, textvariable=self.token_var, show="*", width=30, bg=SURFACE, fg=FG, insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(tr, text="Use", command=self.do_token_auth, bg=SURFACE, fg=FG, relief=tk.RAISED, padx=8, activebackground="#45475a", activeforeground=FG).pack(side=tk.LEFT)
        if self.cfg.get("token"):
            ttk.Label(self.inner, text="  Authenticated: @" + self.cfg.get("username", "?"), style="Status.TLabel").pack(anchor=tk.W)

        self.sec("LOCAL FOLDER")
        pr = ttk.Frame(self.inner); pr.pack(fill=tk.X, pady=2)
        self.path_var = tk.StringVar(value=self.local_path)
        tk.Entry(pr, textvariable=self.path_var, bg=SURFACE, fg=FG, insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(pr, text="Browse", command=self.browse_folder, bg=SURFACE, fg=FG, relief=tk.RAISED, padx=8, activebackground="#45475a", activeforeground=FG).pack(side=tk.LEFT)

        if not self.existing:
            self.sec("REPOSITORY")
            nr = ttk.Frame(self.inner); nr.pack(fill=tk.X, pady=2)
            ttk.Label(nr, text="  Name: ").pack(side=tk.LEFT)
            self.name_var = tk.StringVar(value=self.repo_name)
            tk.Entry(nr, textvariable=self.name_var, bg=SURFACE, fg=FG, insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, padx=5, ipady=2)
            dr = ttk.Frame(self.inner); dr.pack(fill=tk.X, pady=2)
            ttk.Label(dr, text="  Desc: ").pack(side=tk.LEFT)
            self.desc_var = tk.StringVar(value=self.cfg.get("description", ""))
            tk.Entry(dr, textvariable=self.desc_var, bg=SURFACE, fg=FG, insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=2)
            vr = ttk.Frame(self.inner); vr.pack(fill=tk.X, pady=2)
            ttk.Label(vr, text="  Visibility: ").pack(side=tk.LEFT)
            self.vis_var = tk.StringVar(value=self.cfg.get("visibility", "public"))
            ttk.Radiobutton(vr, text="Public", value="public", variable=self.vis_var).pack(side=tk.LEFT, padx=8)
            ttk.Radiobutton(vr, text="Private", value="private", variable=self.vis_var).pack(side=tk.LEFT, padx=8)
            lr = ttk.Frame(self.inner); lr.pack(fill=tk.X, pady=2)
            ttk.Label(lr, text="  License: ").pack(side=tk.LEFT)
            self.license_var = tk.StringVar(value=self.cfg.get("license", "MIT"))
            for lic in ["MIT", "GPL-3.0", "Apache-2.0", "None"]:
                ttk.Radiobutton(lr, text=lic, value=lic, variable=self.license_var).pack(side=tk.LEFT, padx=6)

            self.sec("AUTO-GENERATE FILES")
            self.scheck("README.md", "Project info, quick start", "readme")
            self.scheck("LICENSE", "MIT / GPL / Apache", "license")
            self.scheck("CONTRIBUTING.md", "Fork/branch/PR guidelines", "contributing")
            self.scheck("CHANGELOG.md", "Keep-a-Changelog format", "changelog")
            self.scheck(".gitignore", "Python, IDE, OS patterns", "gitignore")
            self.scheck(".gitattributes", "Text/binary detection", "gitattributes")
            self.scheck(".editorconfig", "UTF-8, LF, 4-space", "editorconfig")
            self.scheck("NOTES.md", "Dev notes + TODO", "notes")
            self.scheck("ISSUE_TEMPLATE", "Bug report template", "issue")
            self.scheck("PR_TEMPLATE", "PR checklist", "pr")
            self.scheck("CI workflow (GitHub Actions)", "Lint + test on push", "cicd")
        else:
            self.sec("REPO STATUS")
            self.status_info = tk.StringVar(value="")
            ttk.Label(self.inner, textvariable=self.status_info, foreground=GREEN, font=("Arial", 9), background=BG, justify=tk.LEFT).pack(anchor=tk.W, pady=2)
            self.show_status()

    def sec(self, title):
        ttk.Separator(self.inner, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 2))
        ttk.Label(self.inner, text=title, style="Section.TLabel").pack(anchor=tk.W)

    def scheck(self, label, detail, key):
        row = ttk.Frame(self.inner); row.pack(fill=tk.X, pady=1, padx=2)
        ttk.Checkbutton(row, text="  " + label + "  ", variable=self.sv[key]).pack(side=tk.LEFT)
        ttk.Label(row, text=detail, style="Sub.TLabel").pack(side=tk.LEFT, padx=(6, 0))

    def browse_folder(self):
        p = filedialog.askdirectory(initialdir=self.local_path or os.path.expanduser("~"))
        if p:
            self.path_var.set(p)
            self.local_path = p
            self.existing = is_git_repo(p)
            if self.existing:
                self.show_status()

    def show_status(self):
        p = self.path_var.get().strip()
        if not p: return
        info = "  Branch: " + get_branch(p) + "\n  Remote: " + (get_remote_url(p) or "(none)") + "\n  Uncommitted: " + str(len(get_status(p)))
        self.status_info.set(info)

    def do_browser_auth(self):
        if not CLIENT_ID:
            messagebox.showerror("Not Configured", "Set GITHUB_CLIENT_ID env var.\nGo to github.com/settings/developers")
            return
        self.status.set("Starting browser auth...")
        self.root.update()
        try:
            df = DeviceFlow(CLIENT_ID)
            df.start()
            webbrowser.open(df.uri + "/" + df.user_code)
            self.status.set("Waiting... Code: " + df.user_code)
            self.root.update()
            def poll():
                end = time.time() + df.expiry
                while time.time() < end:
                    time.sleep(df.interval)
                    try:
                        r = df.poll()
                        if r.get("access_token"):
                            self.root.after(0, lambda: self._auth_ok(r["access_token"], "browser"))
                            return
                        elif r.get("error") in ("authorization_pending", "slow_down"):
                            continue
                        else:
                            self.root.after(0, lambda: messagebox.showerror("Auth Failed", r.get("error", "?")))
                            return
                    except Exception as e:
                        self.root.after(0, lambda ex=str(e): messagebox.showerror("Error", ex))
                        return
                self.root.after(0, lambda: messagebox.showerror("Timeout", "Browser auth timed out."))
            threading.Thread(target=poll, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_token_auth(self):
        t = self.token_var.get().strip()
        if not t:
            messagebox.showerror("Auth", "Paste token (ghp_...)\ngithub.com/settings/tokens\nScope: repo")
            return
        self.status.set("Verifying...")
        self.root.update()
        try:
            gh = GitHub(t)
            u = gh.get_user()
            self._auth_ok(t, "token", u)
        except Exception as e:
            messagebox.showerror("Auth Failed", str(e))

    def _auth_ok(self, token, method, user=None):
        if not user:
            self.gh = GitHub(token)
            user = self.gh.get_user()
        self.cfg["token"] = token
        self.cfg["username"] = user["login"]
        self.cfg["auth_method"] = method
        save_config(self.cfg)
        self.status.set("Authenticated: @" + user["login"] + " (" + method + ")")
        messagebox.showinfo("Done", "Authenticated as @" + user["login"] + "\nMethod: " + method)

    def ensure_auth(self):
        if self.cfg.get("token"):
            self.gh = GitHub(self.cfg["token"])
            try:
                self.gh.get_user()
                return self.gh.user
            except:
                pass
        if CLIENT_ID:
            self.do_browser_auth()
            for _ in range(100):
                self.root.update(); time.sleep(0.1)
                if self.cfg.get("token"):
                    self.gh = GitHub(self.cfg["token"])
                    return self.gh.get_user()
        self.do_token_auth()
        for _ in range(100):
            self.root.update(); time.sleep(0.1)
            if self.cfg.get("token"):
                self.gh = GitHub(self.cfg["token"])
                return self.gh.get_user()
        return None

    def write_file(self, base, rel, content):
        full = os.path.join(base, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if not os.path.exists(full):
            with open(full, "w") as f:
                f.write(content)

    def generate_scaffold(self, path, name, desc, username):
        year = datetime.now().year
        lic = self.license_var.get()
        gen = []
        if self.sv["readme"].get():
            self.write_file(path, "README.md", gen_readme(name, desc, username, lic))
            gen.append("README.md")
        if self.sv["license"].get() and lic != "None":
            if lic == "GPL-3.0":
                self.write_file(path, "LICENSE", gen_license_gpl(username, year))
            else:
                self.write_file(path, "LICENSE", gen_license_mit(username, year))
            gen.append("LICENSE")
        if self.sv["contributing"].get():
            self.write_file(path, "CONTRIBUTING.md", gen_contributing(name))
            gen.append("CONTRIBUTING.md")
        if self.sv["changelog"].get():
            self.write_file(path, "CHANGELOG.md", gen_changelog())
            gen.append("CHANGELOG.md")
        if self.sv["gitignore"].get():
            self.write_file(path, ".gitignore", gen_gitignore())
            gen.append(".gitignore")
        if self.sv["gitattributes"].get():
            self.write_file(path, ".gitattributes", gen_gitattributes())
            gen.append(".gitattributes")
        if self.sv["editorconfig"].get():
            self.write_file(path, ".editorconfig", gen_editorconfig())
            gen.append(".editorconfig")
        if self.sv["notes"].get():
            self.write_file(path, "NOTES.md", gen_notes(name))
            gen.append("NOTES.md")
        if self.sv["issue"].get():
            self.write_file(path, ".github/ISSUE_TEMPLATE/bug_report.md", gen_issue_template())
            gen.append("ISSUE_TEMPLATE")
        if self.sv["pr"].get():
            self.write_file(path, ".github/PULL_REQUEST_TEMPLATE.md", gen_pr_template())
            gen.append("PR_TEMPLATE")
        if self.sv["cicd"].get():
            self.write_file(path, ".github/workflows/ci.yml", gen_cicd(name))
            gen.append("CI workflow")
        return gen

    def do_create(self):
        user = self.ensure_auth()
        if not user: return
        path = self.path_var.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showerror("Error", "Select a valid folder."); return
        name = self.name_var.get().strip() or os.path.basename(path)
        desc = self.desc_var.get().strip()
        private = self.vis_var.get() == "private"
        self.cfg.update({"local_path": path, "repo_name": name, "description": desc, "visibility": self.vis_var.get(), "license": self.license_var.get()})
        save_config(self.cfg)
        if not self.gh.repo_exists(name):
            self.status.set("Creating repo...")
            self.root.update()
            try:
                self.gh.create_repo(name, desc, private)
            except Exception as e:
                messagebox.showerror("GitHub", str(e)); return
        try:
            self.status.set("Generating files...")
            self.root.update()
            gen = self.generate_scaffold(path, name, desc, user["login"])
            if not is_git_repo(path):
                git_run(path, "init", "-b", "main")
                git_run(path, "config", "user.name", user["login"])
                git_run(path, "config", "user.email", user["login"] + "@users.noreply.github.com")
            git_run(path, "add", "-A")
            git_run(path, "commit", "-m", "Initial: " + name + " (" + str(len(gen)) + " files)")
            token = self.cfg["token"]
            remote = "https://" + token + "@github.com/" + user["login"] + "/" + name + ".git"
            ex = get_remote_url(path)
            if ex:
                git_run(path, "remote", "set-url", "origin", remote)
            else:
                git_run(path, "remote", "add", "origin", remote)
            self.status.set("Pushing...")
            self.root.update()
            r = git_run(path, "push", "-u", "origin", "main")
            if r.returncode != 0:
                git_run(path, "remote", "set-url", "origin", "https://github.com/" + user["login"] + "/" + name + ".git")
                r = git_run(path, "push", "-u", "origin", "main")
                if r.returncode != 0:
                    messagebox.showerror("Push Failed", r.stderr); return
            git_run(path, "remote", "set-url", "origin", "https://github.com/" + user["login"] + "/" + name + ".git")
            self.status.set("Done: github.com/" + user["login"] + "/" + name)
            fl = "\n".join("  " + g for g in gen)
            messagebox.showinfo("Done", "Created & pushed!\n\n  github.com/" + user["login"] + "/" + name + "\n\nFiles:\n" + fl)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_push(self):
        p = self.path_var.get().strip()
        if not is_git_repo(p):
            messagebox.showerror("Error", "Not a git repo."); return
        git_run(p, "add", "-A")
        git_run(p, "commit", "-m", "Sync: " + os.path.basename(p))
        r = git_run(p, "push")
        if r.returncode != 0:
            messagebox.showerror("Push Failed", r.stderr)
        else:
            self.status.set("Pushed"); self.show_status()

    def do_pull(self):
        p = self.path_var.get().strip()
        if not is_git_repo(p):
            messagebox.showerror("Error", "Not a git repo."); return
        r = git_run(p, "pull", "--rebase")
        if r.returncode != 0:
            messagebox.showerror("Pull Failed", r.stderr)
        else:
            self.status.set("Pulled"); self.show_status()

    def do_sync(self):
        self.do_pull()
        if self.status.get() == "Pulled":
            self.do_push()

    def do_reset(self):
        if messagebox.askyesno("Reset", "Clear saved config?"):
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            self.cfg = {}
            self.token_var.set("")
            self.path_var.set("")
            self.local_path = ""
            self.existing = False
            self.status.set("Cleared")


if __name__ == "__main__":
    if not git_available():
        print("ERROR: git not found. Run: sudo apt install git")
        sys.exit(1)
    root = tk.Tk()
    GHSetup(root)
    root.mainloop()   
