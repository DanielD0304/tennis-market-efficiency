"""Startskripte für die Aufgabenplanung (#35): Sie dürfen keinen absoluten Pfad enthalten.

Der alte Stand lag unter data/ (nicht versioniert) und zeigte fest auf den Ordner vor dem Repo-Umzug. Danach liefen
Collector, Paper-Loop und Nightly wochenlang ins Leere, ohne dass es auffiel.
"""
import re
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / 'scripts' / 'windows'
FILES = sorted(p for p in SCRIPTS.iterdir() if p.is_file())
CMDS = [p for p in FILES if p.suffix == '.cmd']

# Laufwerksbuchstabe mit Pfad (C:\..., C:/...) oder Benutzerordner. Platzhalter in Kommentaren gelten nicht.
ABSOLUTE = re.compile(r'\b[A-Za-z]:[\\/]|\\Users\\|OneDrive')


def test_skripte_vorhanden():
    names = {p.name for p in FILES}
    assert {'nightly.cmd', 'paper.cmd', 'odds_api.cmd', 'run_hidden.vbs', 'install_tasks.cmd',
            'install_tasks.ps1'} <= names


@pytest.mark.parametrize('path', FILES, ids=lambda p: p.name)
def test_kein_absoluter_pfad(path):
    for nr, line in enumerate(path.read_text(encoding='ascii').splitlines(), 1):
        code = line.split('rem ', 1)[0] if path.suffix == '.cmd' else line
        if path.suffix in ('.ps1', '.vbs'):
            code = code.split('#' if path.suffix == '.ps1' else "'", 1)[0]
        assert not ABSOLUTE.search(code), f'{path.name}:{nr}: absoluter Pfad: {line.strip()}'


@pytest.mark.parametrize('path', FILES, ids=lambda p: p.name)
def test_ascii_und_crlf(path):
    """cmd.exe liest in der OEM-Codepage, PowerShell 5.1 ohne BOM in ANSI: Umlaute würden zerbrechen."""
    raw = path.read_bytes()
    raw.decode('ascii')
    if path.suffix == '.cmd':
        assert raw.count(b'\n') == raw.count(b'\r\n'), f'{path.name}: Zeilenenden müssen CRLF sein'


@pytest.mark.parametrize('path', [p for p in CMDS if p.name != 'install_tasks.cmd'], ids=lambda p: p.name)
def test_laufskripte_wechseln_ins_repo(path):
    """Jedes Laufskript wechselt relativ zu seinem eigenen Ort ins Repo und nimmt Python aus einer Variable."""
    text = path.read_text(encoding='ascii')
    assert r'cd /d "%~dp0..\.."' in text
    assert 'if not defined TENNIS_PYTHON set "TENNIS_PYTHON=py -3"' in text
    assert re.search(r'%TENNIS_PYTHON% -m src\.', text)


def test_paper_laeuft_als_dauerprozess():
    assert '-m src.paper.run --loop 30' in (SCRIPTS / 'paper.cmd').read_text(encoding='ascii')
