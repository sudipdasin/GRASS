#!/usr/bin/env python3
"""
gh-setup.py v2 — GitHub Repo Auto Setup & Sync
Auth: Browser (Device Flow) OR Manual Token
Double-click to run. Stdlib only (no pip installs).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import json
import sys
import urllib.request
import urllib.error
import urllib.parse
import webbrowser
import time
import threading
import shutil

# ============================================================
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

# Your GitHub OAuth App client_id (create at https://github.com/settings/developers)
# Device Flow only needs client_id — NO secret required
CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")
# Fallback: if you don't have an OAuth app, leave empty → token paste only
# ============================================================


# ============================================================
# GitHub API
# ============================================================
class GitHub:
    def __init__(self, token):
        self.token = token
        self.user = None

    def _request(self, method, path, data=None, headers_extra=None):
        url = f"{GITHUB_API}{path}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "gh-setup"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        if headers_extra:
            headers.update(headers_extra)
        body = None
        if data:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status == 204:
                    return None
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            try:
                err = json.loads(err_body)
                raise Exception(err.get("message", err_body))
            except json.JSONDecodeError:
                raise Exception(f"HTTP {e.code}")

    def get_user(self):
        self.user = self._request("GET", "/user")
        return self.user

    def create_repo(self, name, description, private):
        return self._request("POST", "/user/repos", {"name": name, "description": description, "private": private})

    def repo_exists(self, name):
        try:
            self._request("GET", f"/repos/{self.user['login']}/{name}")
            return True
        except Exception:
            return False


# ============================================================
# Device Flow (browser auth)
# ============================================================
class DeviceFlow:
    def __init__(self, client_id):
        self.client_id = client_id
        self.device_code = None
        self.user_code = None
        self.verification_uri = None
        self.interval = 5
        self.expiry = 900

    def start(self):
        data = json.dumps({"client_id": self.client_id, "scope": "repo"}).encode()
        req = urllib.request.Request(
            f"{GITHUB_API}/login/device/code",
            data=data,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            r = json.loads(resp.read().decode())
            self.device_code = r["device_code"]
            self.user_code = r["user_code"]
            self.verification_uri = r["verification_uri"]
            self.interval = r.get("interval", 5)
            self.expiry = r.get("expires_in", 900)
            return r

    def poll(self):
        data = json.dumps({
            "client_id": self.client_id,
            "device_code": self.device_code
        }).encode()
        req = urllib.request.Request(
            f"{GITHUB_API}/login/oauth/access_token",
            data=data,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())


# ============================================================
# Git helpers
# ============================================================
def git_available():
    return shutil.which("git") is not None

def git_run(cwd, *args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=cwd)

def is_git_repo(path):
    return os.path.exists(os.path.join(path, ".git"))

def get_remote_url(path):
    r = git_run(path, "remote", "get-url", "origin")
    return r.stdout.strip() if r.returncode == 0 else None

def get_status(path):
    r = git_run(path, "status", "--porcelain")
    return [l for l in r.stdout.strip().split("\n") if l]

def get_branch(path):
    r = git_run(path, "rev-parse", "--abbrev-ref", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else "main"


# ============================================================
# Config
# ============================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


# ============================================================
# UI
# ============================================================
class GHSetup:
    def __init__(self, root):
        self.root = root
        root.title("GitHub Repo Setup & Sync")
        root.geometry("660x740")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background=BG)
        self.style.configure("TLabel", background=BG, foreground=FG, font=("Arial", 10))
        self.style.configure("Title.TLabel", background=BG, foreground=FG, font=("Arial", 14, "bold"))
        self.style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Arial", 9))
        self.style.configure("Section.TLabel", background=BG, foreground=ACCENT, font=("Arial", 10, "bold"))
        self.style.configure("TEntry", fieldbackground=SURFACE, foreground=FG, font=("Arial", 10))
        self.style.configure("TCheckbutton", background=BG, foreground=FG, font=("Arial", 9))
        self.style.configure("TRadiobutton", background=BG, foreground=FG, font=("Arial", 9))
        self.style.configure("Status.TLabel", background=BG, foreground=GREEN, font=("Arial", 9))

        self.cfg = load_config()
        self.gh = None
        self.local_path = self.cfg.get("local_path", "")
        self.repo_name = self.cfg.get("repo_name", "")
        self.existing = self.local_path and is_git_repo(self.local_path)

        self.build_ui()

    def build_ui(self):
        ttk.Label(self.root, text="⚙ GitHub Repo Setup & Sync", style="Title.TLabel").pack(anchor=tk.W, padx=15, pady=(12, 2))
        ttk.Label(self.root, text="Create on first run · Sync on subsequent runs", style="Sub.TLabel").pack(anchor=tk.W, padx=15)

        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # === AUTH ===
        self.section(main, "🔑  AUTHENTICATION")
        auth_frame = ttk.Frame(main)
        auth_frame.pack(fill=tk.X, pady=2)

        # Method selector
        self.auth_method = tk.StringVar(value="browser" if CLIENT_ID else "token")
        ttk.Radiobutton(auth_frame, text="🌐 Browser (Device Flow)", value="browser",
                        variable=self.auth_method, style="TRadiobutton").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(auth_frame, text="🔑 Paste Token", value="token",
                        variable=self.auth_method, style="TRadiobutton").pack(side=tk.LEFT)

        # Browser auth area
        self.browser_frame = ttk.Frame(main)
        self.browser_frame.pack(fill=tk.X, pady=2)
        if CLIENT_ID:
            tk.Button(self.browser_frame, text="  🌐  Login via Browser  ",
                      command=self.do_browser_auth,
                      bg=ACCENT, fg=BG, relief=tk.RAISED, bd=2,
                      font=("Arial", 10, "bold"), padx=12, pady=6,
                      activebackground="#74c7ec", activeforeground=BG,
                      cursor="hand2").pack(side=tk.LEFT)
            ttk.Label(self.browser_frame, text="  Opens browser → you authorize → auto-captures token",
                      style="Sub.TLabel").pack(side=tk.LEFT, padx=8)
        else:
            ttk.Label(self.browser_frame, text="  (Set GITHUB_CLIENT_ID env var to enable browser auth)",
                      style="Sub.TLabel").pack(side=tk.LEFT)

        # Token auth area
        self.token_frame = ttk.Frame(main)
        self.token_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.token_frame, text="  Token: ").pack(side=tk.LEFT)
        self.token_var = tk.StringVar(value=self.cfg.get("token", ""))
        tk.Entry(self.token_frame, textvariable=self.token_var, show="•", width=35,
                 bg=SURFACE, fg=FG, insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.token_frame, text="Use", command=self.do_token_auth,
                  bg=SURFACE, fg=FG, relief=tk.RAISED, padx=8,
                  activebackground="#45475a", activeforeground=FG).pack(side=tk.LEFT)
        ttk.Label(self.token_frame, text="  ghp_… (scope: repo)", style="Sub.TLabel").pack(side=tk.LEFT, padx=5)

        # Auth status
        if self.cfg.get("token"):
            self.auth_status_lbl = ttk.Label(main, text=f"  ✓ Authenticated: @{self.cfg.get('username', '?')}", style="Status.TLabel")
            self.auth_status_lbl.pack(anchor=tk.W)

        # === LOCAL FOLDER ===
        self.section(main, "📁  LOCAL PROJECT FOLDER")
        path_row = ttk.Frame(main)
        path_row.pack(fill=tk.X, pady=2)
        self.path_var = tk.StringVar(value=self.local_path)
        tk.Entry(path_row, textvariable=self.path_var, bg=SURFACE, fg=FG,
                 insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(path_row, text="Browse…", command=self.browse_folder,
                  bg=SURFACE, fg=FG, relief=tk.RAISED, padx=8,
                  activebackground="#45475a", activeforeground=FG).pack(side=tk.LEFT)

        # === REPO DETAILS (first run only) ===
        if not self.existing:
            self.section(main, "📦  REPOSITORY DETAILS")
            name_row = ttk.Frame(main)
            name_row.pack(fill=tk.X, pady=2)
            ttk.Label(name_row, text="  Name: ").pack(side=tk.LEFT)
            self.name_var = tk.StringVar(value=self.repo_name)
            tk.Entry(name_row, textvariable=self.name_var, bg=SURFACE, fg=FG,
                     insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, padx=5, ipady=2)

            desc_row = ttk.Frame(main)
            desc_row.pack(fill=tk.X, pady=2)
            ttk.Label(desc_row, text="  Desc: ").pack(side=tk.LEFT)
            self.desc_var = tk.StringVar(value=self.cfg.get("description", ""))
            tk.Entry(desc_row, textvariable=self.desc_var, bg=SURFACE, fg=FG,
                     insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=2)

            vis_row = ttk.Frame(main)
            vis_row.pack(fill=tk.X, pady=2)
            ttk.Label(vis_row, text="  Visibility: ").pack(side=tk.LEFT)
            self.vis_var = tk.StringVar(value=self.cfg.get("visibility", "public"))
            ttk.Radiobutton(vis_row, text="Public", value="public", variable=self.vis_var).pack(side=tk.LEFT, padx=8)
            ttk.Radiobutton(vis_row, text="Private", value="private", variable=self.vis_var).pack(side=tk.LEFT, padx=8)

            self.section(main, "📄  FILES")
            self.filter_var = tk.StringVar(value=self.cfg.get("filter", "*"))
            f_row = ttk.Frame(main)
            f_row.pack(fill=tk.X, pady=2)
            ttk.Label(f_row, text="  Include: ").pack(side=tk.LEFT)
            tk.Entry(f_row, textvariable=self.filter_var, bg=SURFACE, fg=FG,
                     insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            self.exclude_var = tk.StringVar(value=self.cfg.get("exclude", "__pycache__,*.pyc,.git"))
            e_row = ttk.Frame(main)
            e_row.pack(fill=tk.X, pady=2)
            ttk.Label(e_row, text="  Exclude: ").pack(side=tk.LEFT)
            tk.Entry(e_row, textvariable=self.exclude_var, bg=SURFACE, fg=FG,
                     insertbackground=FG, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        else:
            self.section(main, "🔄  REPO STATUS")
            self.status_info = tk.StringVar(value="")
            ttk.Label(main, textvariable=self.status_info, foreground=GREEN,
                      font=("Arial", 9), background=BG, justify=tk.LEFT).pack(anchor=tk.W, pady=2)
            self.show_existing_status()

        # === BUTTONS ===
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        if self.existing:
            tk.Button(btn_frame, text="  ⬆  PUSH  ", command=self.do_push,
                      bg=GREEN, fg=BG, relief=tk.RAISED, bd=2,
                      font=("Arial", 11, "bold"), padx=15, pady=7,
                      activebackground="#94e2d5", activeforeground=BG, cursor="hand2").pack(side=tk.LEFT, padx=(0, 6))
            tk.Button(btn_frame, text="  ⬇  PULL  ", command=self.do_pull,
                      bg=ACCENT, fg=BG, relief=tk.RAISED, bd=2,
                      font=("Arial", 11, "bold"), padx=15, pady=7,
                      activebackground="#74c7ec", activeforeground=BG, cursor="hand2").pack(side=tk.LEFT, padx=3)
            tk.Button(btn_frame, text="  ⇅  SYNC  ", command=self.do_sync,
                      bg=YELLOW, fg=BG, relief=tk.RAISED, bd=2,
                      font=("Arial", 11, "bold"), padx=15, pady=7,
                      activebackground="#f9e2af", activeforeground=BG, cursor="hand2").pack(side=tk.LEFT, padx=3)
        else:
            tk.Button(btn_frame, text="  ✓  CREATE + PUSH  ", command=self.do_create,
                      bg=GREEN, fg=BG, relief=tk.RAISED, bd=2,
                      font=("Arial", 11, "bold"), padx=15, pady=7,
                      activebackground="#94e2d5", activeforeground=BG, cursor="hand2").pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame, text="  ↺  RESET  ", command=self.do_reset,
                  bg=RED, fg=BG, relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"), padx=10, pady=7,
                  activebackground="#eba0ac", activeforeground=BG, cursor="hand2").pack(side=tk.RIGHT, padx=(6, 0))

        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status, style="Status.TLabel").pack(fill=tk.X, padx=15, pady=(0, 8))

    def section(self, parent, title):
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 2))
        ttk.Label(parent, text=title, style="Section.TLabel").pack(anchor=tk.W)

    # === AUTH: Browser (Device Flow) ===
    def do_browser_auth(self):
        if not CLIENT_ID:
            messagebox.showerror("Not Configured",
                "Browser auth requires a GitHub OAuth App.\n\n"
                "1. Go to https://github.com/settings/developers\n"
                "2. New OAuth App\n"
                "3. Name: gh-setup\n"
                "4. Homepage: http://localhost\n"
                "5. Copy the Client ID\n\n"
                "Then set it before running:\n"
                "  export GITHUB_CLIENT_ID=your_id_here\n"
                "  python3 ~/gh-setup.py\n\n"
                "Or add to ~/.bashrc:\n"
                "  export GITHUB_CLIENT_ID=your_id_here")
            return

        self.status.set("Starting browser auth…")
        self.root.update()

        try:
            df = DeviceFlow(CLIENT_ID)
            r = df.start()
            code = df.user_code
            uri = df.verification_uri

            # Open browser
            webbrowser.open(f"{uri}/{code}")

            # Show waiting dialog
            self.status.set(f"Waiting for browser auth… Code: {code}")
            self.root.update()

            # Poll in background
            def poll_thread():
                end_time = time.time() + df.expiry
                while time.time() < end_time:
                    time.sleep(df.interval)
                    try:
                        result = df.poll()
                        if result.get("access_token"):
                            token = result["access_token"]
                            self.root.after(0, lambda: self._auth_success(token, "browser"))
                            return
                        elif result.get("error") == "authorization_pending":
                            continue
                        elif result.get("error") == "slow_down":
                            time.sleep(5)
                            continue
                        else:
                            err = result.get("error", "unknown")
                            self.root.after(0, lambda e=err: messagebox.showerror("Auth Failed", f"Device flow error: {e}"))
                            self.root.after(0, lambda: self.status.set("Auth failed"))
                            return
                    except Exception as e:
                        self.root.after(0, lambda ex=str(e): messagebox.showerror("Auth Error", ex))
                        return
                # Timeout
                self.root.after(0, lambda: messagebox.showerror("Timeout", "Browser auth timed out.\nTry again or use token paste."))
                self.root.after(0, lambda: self.status.set("Auth timed out"))

            threading.Thread(target=poll_thread, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Browser Auth Error", str(e))
            self.status.set("Error")

    # === AUTH: Token paste ===
    def do_token_auth(self):
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("Auth", "Paste your GitHub token (ghp_…).\n\nCreate at: https://github.com/settings/tokens\nScope: repo")
            return
        self.status.set("Verifying token…")
        self.root.update()
        try:
            gh = GitHub(token)
            user = gh.get_user()
            self._auth_success(token, "token", user)
        except Exception as e:
            messagebox.showerror("Auth Failed", f"Token rejected:\n{e}")
            self.status.set("Auth failed")

    # === Shared auth success ===
    def _auth_success(self, token, method, user=None):
        if not user:
            self.gh = GitHub(token)
            user = self.gh.get_user()
        self.cfg["token"] = token
        self.cfg["username"] = user["login"]
        self.cfg["auth_method"] = method
        save_config(self.cfg)
        self.status.set(f"✓ Authenticated as @{user['login']} (via {method})")
        messagebox.showinfo("Authenticated", f"✓ Logged in as @{user['login']}\n\nMethod: {method}\nToken saved locally.")

    # === FOLDER ===
    def browse_folder(self):
        path = filedialog.askdirectory(initialdir=self.local_path or os.path.expanduser("~"))
        if path:
            self.path_var.set(path)
            self.local_path = path
            self.existing = is_git_repo(path)
            if self.existing:
                self.show_existing_status()

    def show_existing_status(self):
        path = self.path_var.get().strip()
        if not path:
            return
        remote = get_remote_url(path)
        branch = get_branch(path)
        changes = get_status(path)
        info = f"  Branch: {branch}\n  Remote: {remote or '(none)'}\n  Uncommitted: {len(changes)}"
        if changes:
            info += "\n" + "\n".join(f"    {c[:60]}" for c in changes[:5])
            if len(changes) > 5:
                info += f"\n    …+{len(changes)-5} more"
        self.status_info.set(info)

    # === ACTIONS ===
    def ensure_auth(self):
        if self.cfg.get("token"):
            self.gh = GitHub(self.cfg["token"])
            try:
                self.gh.get_user()
                return self.gh.user
            except:
                pass
        # Try browser first if available
        if CLIENT_ID and self.auth_method.get() == "browser":
            self.do_browser_auth()
            # Wait a bit
            for _ in range(50):
                self.root.update()
                time.sleep(0.1)
                if self.cfg.get("token"):
                    self.gh = GitHub(self.cfg["token"])
                    return self.gh.get_user()
        # Fallback to token
        self.do_token_auth()
        for _ in range(50):
            self.root.update()
            time.sleep(0.1)
            if self.cfg.get("token"):
                self.gh = GitHub(self.cfg["token"])
                return self.gh.get_user()
        return None

    def do_create(self):
        user = self.ensure_auth()
        if not user:
            return
        path = self.path_var.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showerror("Error", "Select a valid folder.")
            return
        name = self.name_var.get().strip() or os.path.basename(path)
        desc = self.desc_var.get().strip()
        private = self.vis_var.get() == "private"

        self.cfg.update({"local_path": path, "repo_name": name, "description": desc,
                         "visibility": self.vis_var.get(), "filter": self.filter_var.get(),
                         "exclude": self.exclude_var.get()})
        save_config(self.cfg)

        if not self.gh.repo_exists(name):
            self.status.set(f"Creating '{name}'…")
            self.root.update()
            try:
                self.gh.create_repo(name, desc, private)
            except Exception as e:
                messagebox.showerror("GitHub", str(e))
                return

        try:
            if not is_git_repo(path):
                git_run(path, "init", "-b", "main")
                git_run(path, "config", "user.name", user["login"])
                git_run(path, "config", "user.email", f"{user['login']}@users.noreply.github.com")
            exclude = self.exclude_var.get().strip()
            if exclude:
                with open(os.path.join(path, ".gitignore"), "w") as f:
                    f.write("\n".join(exclude.split(",")) + "\n")
            git_run(path, "add", "-A")
            git_run(path, "commit", "-m", f"Initial: {name}")
            token = self.cfg["token"]
            remote = f"https://{token}@github.com/{user['login']}/{name}.git"
            existing = get_remote_url(path)
            if existing:
                git_run(path, "remote", "set-url", "origin", remote)
            else:
                git_run(path, "remote", "add", "origin", remote)
            self.status.set("Pushing…")
            self.root.update()
            r = git_run(path, "push", "-u", "origin", "main")
            if r.returncode != 0:
                git_run(path, "remote", "set-url", "origin", f"https://github.com/{user['login']}/{name}.git")
                r = git_run(path, "push", "-u", "origin", "main")
                if r.returncode != 0:
                    messagebox.showerror("Push Failed", r.stderr)
                    return
            # Clean token from URL
            git_run(path, "remote", "set-url", "origin", f"https://github.com/{user['login']}/{name}.git")
            self.status.set(f"✓ github.com/{user['login']}/{name}")
            messagebox.showinfo("Done", f"✓ Created & pushed!\n\n  {path}\n  github.com/{user['login']}/{name}\n\nNext run → Push/Pull/Sync")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_push(self):
        path = self.path_var.get().strip()
        if not is_git_repo(path):
            messagebox.showerror("Error", "Not a git repo.")
            return
        git_run(path, "add", "-A")
        git_run(path, "commit", "-m", f"Sync: {os.path.basename(path)}")
        r = git_run(path, "push")
        if r.returncode != 0:
            messagebox.showerror("Push Failed", r.stderr)
        else:
            self.status.set("✓ Pushed")
            self.show_existing_status()

    def do_pull(self):
        path = self.path_var.get().strip()
        if not is_git_repo(path):
            messagebox.showerror("Error", "Not a git repo.")
            return
        r = git_run(path, "pull", "--rebase")
        if r.returncode != 0:
            messagebox.showerror("Pull Failed", r.stderr)
        else:
            self.status.set("✓ Pulled")
            self.show_existing_status()

    def do_sync(self):
        self.do_pull()
        if self.status.get().startswith("✓"):
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
