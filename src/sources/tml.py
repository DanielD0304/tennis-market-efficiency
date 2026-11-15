"""
TennisMyLife (https://stats.tennismylife.org/tennis-match-database): Ergebnisse mit Aufschlag-Stats, Minuten, Runde und
Ranking im Sackmann-Format, täglich gepflegt. Schließt die Lücke nach dem Ende des Sackmann-Archivs (Turnierstart
01.06.2026): ohne diese Quelle haben spätere Matches keine Stats.

Abdeckung: ATP-Haupttour, deren Qualifikation, Challenger und WTA-Haupttour. Kein ITF, kein WTA 125.

Nutzungsbedingungen (Stand 11/2026): nur private, schulische und nicht-kommerzielle Forschung. Kommerzielle Nutzung,
ausdrücklich auch Vorhersagemodelle für kommerzielle Dienste und monetarisierte Wahrscheinlichkeiten, braucht eine
schriftliche Erlaubnis von TennisMyLife. Die Rohdateien dürfen nicht weitergegeben werden: data/raw/tml/ bleibt lokal
(data/ steht in .gitignore), Tests nutzen erfundene Zeilen.

Unterschiede zu Sackmann, die load() ausgleicht:
  - 'tourney_date' ist in der ATP-Haupttour-Datei der Tag des Matches, in den Challenger- und WTA-Dateien der
    Turnierstart. Hier wird daraus match_date (wie geliefert) und tourney_date = frühester Tag des Turniers.
    build._window erkennt Turniere ohne Tagesdatum daran, dass match_date dem Turnierstart gleicht.
  - Turnierstufe als Zahl ('250', '500', '1000') statt Sackmann-Code (A, PM, P, I).
  - Spalte 'indoor' (I/O) -> court. Kein Geburtsdatum, dafür das Alter: daraus ein genähertes Geburtsdatum.
  - Laufende Turniere stehen in eigenen Dateien (ONGOING) und erst nach ihrem Ende in der Jahresdatei.
"""
import os
import time
from datetime import datetime, timedelta

from .common import RAW_DIR, http_get, read_csv, status_from_score

BASE_URL = "https://stats.tennismylife.org/data"
DIR = os.path.join(RAW_DIR, "tml")

# Datei-Art je Tour -> Pfad auf dem Server ({year} = Jahr)
FILES = {
    'atp': {'main': '{year}.csv', 'quali': 'atp_quali/{year}_atp_quali.csv', 'challenger': '{year}_challenger.csv'},
    'wta': {'main': '{year}_wta.csv'},
}
ONGOING = {
    'atp': {'main': 'ongoing_tourneys.csv', 'challenger': 'challenger_ongoing_tourneys.csv'},
    'wta': {'main': 'wta_ongoing_tourneys.csv'},
}
# Qualifikationen der Haupttour zählen wie bei Sackmann als 'main'
KIND_LEVEL = {'main': 'main', 'quali': 'main', 'challenger': 'challenger'}
LEVEL_CODES = {
    'atp': {'250': 'A', '500': 'A', '1000': 'M'},
    'wta': {'1000': 'PM', '500': 'P', '250': 'I'},
}
COURTS = {'I': 'Indoor', 'O': 'Outdoor'}
HEADER = b'tourney_id'


def kinds(levels, tour='atp'):
    """Datei-Arten, die für die Level gebraucht werden."""
    return [k for k in FILES[tour] if KIND_LEVEL[k] in levels]


def path(year, tour='atp', kind='main'):
    return os.path.join(DIR, os.path.basename(FILES[tour][kind].format(year=year)))


def ongoing_path(tour='atp', kind='main'):
    return os.path.join(DIR, ONGOING[tour][kind])


def _fresh(target, max_age_hours):
    if not os.path.exists(target):
        return False
    return max_age_hours is None or time.time() - os.path.getmtime(target) < max_age_hours * 3600


def _fetch(name, target):
    r = http_get(f"{BASE_URL}/{name}")
    if r is None or not r.content.lstrip(b'\xef\xbb\xbf').startswith(HEADER):  # Fehlerseiten sind HTML
        return False
    tmp = target + ".tmp"
    with open(tmp, "wb") as f:
        f.write(r.content)
    os.replace(tmp, target)
    return True


def download(years, tour='atp', levels=('main',), max_age_hours=20, ongoing=True):
    """
    Lädt die Jahresdateien und (ongoing) die Dateien der laufenden Turniere. Vorhandene Dateien werden erst neu
    geladen, wenn sie älter als max_age_hours sind (None = nie): die Seite ändert das laufende Jahr täglich.
    Schlägt ein Abruf fehl, bleibt die alte Datei stehen.
    """
    os.makedirs(DIR, exist_ok=True)
    loaded = []
    for kind in kinds(levels, tour):
        for year in years:
            target = path(year, tour, kind)
            if not _fresh(target, max_age_hours) and _fetch(FILES[tour][kind].format(year=year), target):
                loaded.append((kind, year))
        if ongoing and kind in ONGOING[tour]:
            target = ongoing_path(tour, kind)
            if not _fresh(target, max_age_hours) and _fetch(ONGOING[tour][kind], target):
                loaded.append((kind, 'ongoing'))
    return loaded


def _dob(age, day):
    """Genähertes Geburtsdatum 'YYYYMMDD' aus dem Alter in Jahren am Tag des Matches ('' ohne Alter)."""
    try:
        born = datetime.strptime(day, "%Y%m%d") - timedelta(days=float(age) * 365.25)
    except (TypeError, ValueError):
        return ""
    return born.strftime("%Y%m%d")


def _row(r, tour, kind):
    day = (r.get('tourney_date') or '').strip()[:8]
    winner, loser = (r.get('winner_name') or '').strip(), (r.get('loser_name') or '').strip()
    if len(day) != 8 or not day.isdigit() or not winner or not loser:
        return None
    code = (r.get('tourney_level') or '').strip()
    out = dict(r)
    out.update({
        'tour': tour, 'level': KIND_LEVEL[kind], 'source': 'tml',
        'tourney_id': f"tml-{r.get('tourney_id')}",
        'tourney_level': LEVEL_CODES[tour].get(code, code),
        'court': COURTS.get((r.get('indoor') or '').strip(), ''),
        'winner_name': winner, 'loser_name': loser,
        'match_date': day,
        'status': status_from_score(r.get('score')),
        'winner_dob': _dob(r.get('winner_age'), day), 'loser_dob': _dob(r.get('loser_age'), day),
    })
    return out


def load(years, tour='atp', levels=('main',)):
    """
    Matches der gewünschten Level im gemeinsamen Schema (source 'tml'). Fehlende Dateien werden übersprungen. Ein Match,
    das in der Jahresdatei und bei den laufenden Turnieren steht, kommt nur einmal vor (die Jahresdatei gewinnt).
    """
    rows, seen = [], set()
    for kind in kinds(levels, tour):
        files = [path(y, tour, kind) for y in years]
        if kind in ONGOING[tour]:
            files.append(ongoing_path(tour, kind))
        for p in files:
            if not os.path.exists(p):
                continue
            for r in read_csv(p):
                row = _row(r, tour, kind)
                if row is None:
                    continue
                key = (row['tourney_id'], row.get('round'), row['winner_name'], row['loser_name'])
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
    # Turnierstart = frühester Tag des Turniers (Qualifikation eingeschlossen)
    start = {}
    for r in rows:
        start[r['tourney_id']] = min(start.get(r['tourney_id'], r['match_date']), r['match_date'])
    for r in rows:
        r['tourney_date'] = start[r['tourney_id']]
    return rows
