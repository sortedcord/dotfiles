#!/usr/bin/env python3
"""Install this user's theme, or restore a backup using --restore PATH."""
import argparse
import configparser
from datetime import datetime
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
SCHEMA = 'org.gnome.desktop.interface'
THEME = HOME / '.local/share/themes/Wedgewood'
FILES = [HOME / '.config' / f'gtk-{version}' / name
         for version in ('3.0', '4.0') for name in ('settings.ini', 'gtk.css')]

def setting(key, value=None):
    command = ['gsettings', 'get' if value is None else 'set', SCHEMA, key]
    if value is not None:
        command.append(value)
    return subprocess.check_output(command, text=True).strip()

def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--restore', type=Path)
args = parser.parse_args()
if args.restore:
    backup = args.restore.resolve()
    state = json.loads((backup / 'state.json').read_text())
    for record in state['files']:
        target = Path(record['path'])
        remove(target)
        if record['exists']:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup / record['saved'], target, follow_symlinks=False)
    for key, value in state['settings'].items():
        setting(key, value)
    # The inactive installed theme is deliberately kept for future reuse.
    print(f'Restored settings and user CSS from {backup}')
else:
    if THEME.exists() or THEME.is_symlink():
        if not THEME.is_symlink() or THEME.resolve() != ROOT:
            raise SystemExit(f'Refusing to replace existing theme: {THEME}')
    subprocess.run(['python3', str(ROOT / 'build.py')], check=True)
    backup = HOME / '.config' / ('gtk-theme-backup-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    state = {'settings': {key: setting(key) for key in ('gtk-theme', 'color-scheme')}, 'files': []}
    for i, path in enumerate(FILES):
        exists = path.exists() or path.is_symlink()
        record = {'path': str(path), 'exists': exists, 'saved': str(i)}
        if exists:
            shutil.copy2(path, backup / str(i), follow_symlinks=False)
        state['files'].append(record)
    (backup / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
    THEME.parent.mkdir(parents=True, exist_ok=True)
    if not THEME.is_symlink():
        THEME.symlink_to(ROOT, target_is_directory=True)
    for version in ('3.0', '4.0'):
        directory = HOME / '.config' / f'gtk-{version}'
        directory.mkdir(parents=True, exist_ok=True)
        settings = directory / 'settings.ini'
        config = configparser.ConfigParser(interpolation=None)
        config.read(settings)
        if not config.has_section('Settings'):
            config.add_section('Settings')
        config['Settings']['gtk-theme-name'] = 'Wedgewood'
        config['Settings']['gtk-application-prefer-dark-theme'] = 'true'
        if settings.is_symlink():
            settings.unlink()
        with settings.open('w') as stream:
            config.write(stream)
        css = directory / 'gtk.css'
        if css.is_symlink():
            css.unlink()
        # Existing user CSS is backed up, not imported: its colors could win.
        css.write_text(f'/* Wedgewood user palette override. */\n'
                       f'@import url("{(ROOT / f"gtk-{version}" / "palette.css").as_uri()}");\n')
    setting('gtk-theme', 'Wedgewood')
    setting('color-scheme', 'prefer-dark')
    (ROOT / 'last-backup.txt').write_text(str(backup) + '\n')
    print(f'Activated Wedgewood. Backup: {backup}')
    print(f'Undo: python3 {ROOT / "activate.py"} --restore {backup}')
