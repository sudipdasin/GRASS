# gh-setup

Single-file Python GUI that creates, scaffolds, and syncs GitHub repos.
Zero setup. Click Login → Authorize → Done.

## Install

    sudo apt install python3-tk git

## Run

    python3 gh-setup.py

## How it works

1. Select project folder → PROJECT.txt auto-created
2. Import → all fields auto-filled
3. Login via Browser → click Authorize on GitHub
4. CREATE + SCAFFOLD + PUSH
5. Subsequent runs: PUSH / PULL / SYNC

## Features

- Browser-based GitHub auth (Device Flow, no tokens to paste)
- Auto-generates: README, LICENSE, CONTRIBUTING, CHANGELOG,
  .gitignore, .gitattributes, .editorconfig, CI workflow
- Smart defaults (detects language, guesses name from folder)
- Dark theme, no dependencies beyond stdlib

## Requirements

- Python 3.8+
- Git
- python3-tk
- Linux (XFCE/GNOME/KDE)

## License

MIT   
