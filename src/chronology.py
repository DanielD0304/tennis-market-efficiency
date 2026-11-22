"""
Echte Reihenfolge der Matches für Elo, Historien und Features.

Sortiert wird nach dem echten Matchdatum (match_date), fehlt es, nach dem Turnierstart. Innerhalb
eines Tages entscheidet die Runde (R32 vor R16), dann match_num. Sackmann kennt nur den Turnierstart:
alle Matches eines Turniers haben dort dasselbe Datum, die Runde hält sie in der richtigen Folge.
build.py übernimmt das echte Datum aus tennis-data/ESPN, wo dasselbe Match dort vorkommt.

Innerhalb eines Turniers hat deshalb oft nur ein Teil der Matches ein echtes Datum. Ohne Korrektur sortierte ein
Viertelfinale, das nur den Turnierstart kennt, vor die erste Runde desselben Spielers mit echtem Datum, und deren
Features enthielten schon das Ergebnis des Viertelfinales (Issue #76). match_dates gleicht die Daten deshalb je Spieler
und Turnier an die Runden an (_consistent_with_rounds).
"""
import numpy as np
import pandas as pd

from .sources.common import ROUND_ORDER

TOURNEY_KEYS = ('tour', 'tourney_id', 'tourney_date')


def _yyyymmdd(series):
    return pd.to_datetime(series.astype(str).str[:8], format='%Y%m%d', errors='coerce')


def _consistent_with_rounds(df, dates, real):
    """
    Datum je Match, so dass für jeden Spieler innerhalb eines Turniers (TOURNEY_KEYS) eine spätere Runde nie vor einer
    früheren liegt. Zwei Durchgänge je Turnier:
      1. rückwärts: Ein echtes Datum nach dem echten Datum einer späteren Runde desselben Spielers ist ein Datenfehler
         (TennisMyLife-Qualifikationen mit Daten aus dem Hauptfeld). Es wird auf dieses Datum gesenkt. Nie früher als
         die Wahrheit, denn die spätere Runde fand nach der früheren statt.
      2. vorwärts: Jedes Match bekommt mindestens das späteste Datum der früheren Runden seiner Spieler.
    Matches derselben Runde beschränken sich nicht gegenseitig, Matches ohne bekannte Runde (Markt-Zeilen) und ohne
    tourney_id bleiben, wie sie sind. Matches anderer Spieler desselben Turniers beeinflussen das Datum nicht, so wandert
    ein fehlerhaftes Datum nicht durch das Turnier.
    """
    needed = {'round', 'tourney_date', 'winner_name', 'loser_name'}
    if not needed <= set(df.columns):
        return dates
    rank = df['round'].map(ROUND_ORDER).to_numpy(float)
    valid = np.isfinite(rank) & dates.notna().to_numpy()
    if 'tourney_id' in df.columns:
        valid &= df['tourney_id'].notna().to_numpy()
    if valid.sum() < 2:
        return dates
    keys = [k for k in TOURNEY_KEYS if k in df.columns]
    key = df.groupby(keys, sort=False, dropna=False).ngroup().to_numpy()
    # Nur Turniere mit mindestens einem echten Datum: Kennen alle Matches nur den Turnierstart, ändert sich nichts
    valid &= np.isin(key, np.unique(key[valid & real]))
    pos = np.flatnonzero(valid)
    order = pos[np.lexsort((rank[pos], key[pos]))]
    ks, rs = key[order], rank[order]
    winners, losers = df['winner_name'].to_numpy(object), df['loser_name'].to_numpy(object)
    out = dates.to_numpy('datetime64[ns]').copy()
    starts = np.flatnonzero(np.r_[True, ks[1:] != ks[:-1]])
    ends = np.r_[starts[1:], len(order)]
    for a, b in zip(starts, ends):
        if b - a < 2:
            continue
        cut = np.flatnonzero(rs[a + 1:b] != rs[a:b - 1]) + 1
        if not len(cut):
            continue
        rounds = np.split(order[a:b], cut)
        nxt = {}  # Spieler -> frühestes echtes Datum einer späteren Runde
        for grp in reversed(rounds):
            for i in grp:
                if real[i]:
                    later = [nxt[p] for p in (winners[i], losers[i]) if p in nxt]
                    if later and out[i] > min(later):
                        out[i] = min(later)
            for i in grp:
                if real[i]:
                    for p in (winners[i], losers[i]):
                        if p not in nxt or out[i] < nxt[p]:
                            nxt[p] = out[i]
        prev = {}  # Spieler -> spätestes Datum einer früheren Runde
        for grp in rounds:
            for i in grp:
                before = [prev[p] for p in (winners[i], losers[i]) if p in prev]
                if before and out[i] < max(before):
                    out[i] = max(before)
            for i in grp:
                for p in (winners[i], losers[i]):
                    if p not in prev or out[i] > prev[p]:
                        prev[p] = out[i]
    return pd.Series(out, index=df.index)


def match_dates(df):
    """Echtes Matchdatum als Timestamp, sonst Turnierstart; je Spieler und Turnier passend zur Runde."""
    tourney = _yyyymmdd(df['tourney_date'])
    if 'match_date' not in df.columns:
        return tourney
    own = _yyyymmdd(df['match_date'])
    real = (own.notna() & (own != tourney)).to_numpy()
    return _consistent_with_rounds(df, own.fillna(tourney), real)


def chronological(df):
    """df in echter Reihenfolge (Index bleibt erhalten, stabil sortiert)."""
    key = pd.DataFrame({
        'date': match_dates(df),
        'tourney': df['tourney_date'].astype(str).str[:8],
        'round': df['round'].map(ROUND_ORDER).fillna(0) if 'round' in df.columns else 0,
        'num': pd.to_numeric(df['match_num'], errors='coerce').fillna(0) if 'match_num' in df.columns else 0,
    }, index=df.index)
    order = key.sort_values(['date', 'tourney', 'round', 'num'], kind='stable', na_position='first').index
    return df.loc[order]
