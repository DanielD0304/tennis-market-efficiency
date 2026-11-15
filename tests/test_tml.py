"""
Tests für die Quelle TennisMyLife (src/sources/tml.py) und ihre Einbindung in build.py.
Ohne Netz. Alle Zeilen sind erfunden: die echten Dateien dürfen laut Nutzungsbedingungen nicht weitergegeben werden.
"""
import csv
import os
import time

from src.sources import build, tml

HEADER = ['tourney_id', 'tourney_name', 'surface', 'draw_size', 'tourney_level', 'indoor', 'tourney_date',
          'match_num', 'winner_id', 'winner_seed', 'winner_entry', 'winner_name', 'winner_hand', 'winner_ht',
          'winner_ioc', 'winner_age', 'winner_rank', 'winner_rank_points', 'loser_id', 'loser_seed', 'loser_entry',
          'loser_name', 'loser_hand', 'loser_ht', 'loser_ioc', 'loser_age', 'loser_rank', 'loser_rank_points',
          'score', 'best_of', 'round', 'minutes', 'w_ace', 'w_df', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon',
          'w_SvGms', 'w_bpSaved', 'w_bpFaced', 'l_ace', 'l_df', 'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon',
          'l_SvGms', 'l_bpSaved', 'l_bpFaced']


def _line(tid, name, level, day, w, l, rnd='R32', score='6-4 6-4', indoor='O', surface='Hard', num=1, stats=True,
          w_age='25.0', **kw):
    row = {c: '' for c in HEADER}
    row.update({'tourney_id': tid, 'tourney_name': name, 'surface': surface, 'tourney_level': level, 'indoor': indoor,
                'tourney_date': day, 'match_num': num, 'winner_name': w, 'loser_name': l, 'winner_hand': 'R',
                'winner_ioc': 'AAA', 'winner_age': w_age, 'winner_rank': 10, 'loser_hand': 'L', 'loser_ioc': 'BBB',
                'loser_age': '30.5', 'loser_rank': 40, 'score': score, 'best_of': 3, 'round': rnd, 'minutes': 95})
    if stats:
        row.update({'w_ace': 7, 'w_df': 2, 'w_svpt': 70, 'w_1stIn': 45, 'w_1stWon': 34, 'w_2ndWon': 14, 'w_SvGms': 10,
                    'w_bpSaved': 3, 'w_bpFaced': 4, 'l_ace': 3, 'l_df': 4, 'l_svpt': 75, 'l_1stIn': 44,
                    'l_1stWon': 29, 'l_2ndWon': 13, 'l_SvGms': 10, 'l_bpSaved': 5, 'l_bpFaced': 8})
    row.update(kw)
    return row


def _write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)


def _files(tmp_path):
    d = str(tmp_path)
    _write(os.path.join(d, '2026.csv'), [
        # Haupttour: ein Datum je Match
        _line('2026-900', 'Testville Open', '250', '20260914', 'Ann Alpha', 'Bea Beta', 'R32', num=1),
        _line('2026-900', 'Testville Open', '250', '20260916', 'Ann Alpha', 'Cid Gamma', 'R16', '6-3 2-1 RET',
              indoor='I', num=2),
        _line('2026-901', 'Bigtown Masters', '1000', '20261005', 'Dan Delta', 'Eve Epsilon', 'R64', 'W/O', stats=False),
        {**_line('2026-902', 'Kaputt', '250', '', 'X', 'Y')},        # ohne Datum: fällt weg
    ])
    _write(os.path.join(d, '2026_atp_quali.csv'), [
        _line('2026-900', 'Testville Open', '250', '20260912', 'Fay Zeta', 'Gus Eta', 'Q1'),
    ])
    _write(os.path.join(d, '2026_challenger.csv'), [
        # Challenger: alle Matches tragen den Turnierstart
        _line('2026-3000', 'Lima Challenger', 'C', '20260921', 'Hal Theta', 'Ivy Iota', 'R32', surface='Clay'),
        _line('2026-3000', 'Lima Challenger', 'C', '20260921', 'Hal Theta', 'Jon Kappa', 'R16', surface='Clay', num=2),
    ])
    _write(os.path.join(d, 'ongoing_tourneys.csv'), [
        # steht schon in der Jahresdatei
        _line('2026-900', 'Testville Open', '250', '20260914', 'Ann Alpha', 'Bea Beta', 'R32', num=1),
        _line('2026-903', 'Laufend Open', '500', '20261109', 'Ann Alpha', 'Dan Delta', 'R32'),
    ])
    _write(os.path.join(d, '2026_wta.csv'), [
        _line('2026-1100', 'Damenstadt', '1000', '20260914', 'Kim Lambda', 'Lea My', 'R32'),
        _line('2026-1101', 'Kleinstadt', '250', '20260921', 'Kim Lambda', 'Mia Ny', 'R32'),
    ])
    return d


def test_load_maps_to_common_schema(tmp_path, monkeypatch):
    monkeypatch.setattr(tml, 'DIR', _files(tmp_path))
    rows = tml.load([2025, 2026], tour='atp', levels=('main', 'challenger', 'itf'))
    by = {(r['tourney_name'], r['round']): r for r in rows}
    assert len(rows) == 7  # 2 + W/O + Quali + 2 Challenger + 1 laufend, das Doppel und die Zeile ohne Datum fehlen
    assert {r['source'] for r in rows} == {'tml'} and {r['tour'] for r in rows} == {'atp'}

    first, second, quali = by[('Testville Open', 'R32')], by[('Testville Open', 'R16')], by[('Testville Open', 'Q1')]
    # Turnierstart = frühester Tag inklusive Qualifikation, match_date = Tag des Matches
    assert {r['tourney_date'] for r in (first, second, quali)} == {'20260912'}
    assert (first['match_date'], second['match_date'], quali['match_date']) == ('20260914', '20260916', '20260912')
    assert first['tourney_id'] == 'tml-2026-900'
    assert (first['level'], quali['level'], first['tourney_level']) == ('main', 'main', 'A')
    assert (first['court'], second['court']) == ('Outdoor', 'Indoor')
    assert (second['status'], second['score']) == ('RET', '6-3 2-1 RET')
    assert (first['w_svpt'], first['l_bpFaced'], first['minutes']) == ('70', '8', '95')
    # Alter 25,0 am 14.09.2026 -> geboren um den 14.09.2001
    assert first['winner_dob'] in ('20010913', '20010914', '20010915')

    wo = by[('Bigtown Masters', 'R64')]
    assert (wo['status'], wo['tourney_level'], wo['w_svpt']) == ('W/O', 'M', '')
    ch = by[('Lima Challenger', 'R16')]
    assert (ch['level'], ch['tourney_level'], ch['surface']) == ('challenger', 'C', 'Clay')
    assert ch['match_date'] == ch['tourney_date'] == '20260921'  # nur der Turnierstart bekannt
    assert by[('Laufend Open', 'R32')]['tourney_level'] == 'A'

    assert len(tml.load([2026], tour='atp', levels=('main',))) == 5
    assert tml.load([2026], tour='atp', levels=('itf',)) == []
    wta = tml.load([2026], tour='wta', levels=('main', 'challenger'))
    assert [(r['tour'], r['level'], r['tourney_level']) for r in wta] == [('wta', 'main', 'PM'), ('wta', 'main', 'I')]


class _Response:
    def __init__(self, content):
        self.content = content


def test_download_refreshes_and_keeps_old_file_on_error(tmp_path, monkeypatch):
    monkeypatch.setattr(tml, 'DIR', str(tmp_path))
    good = b'tourney_id,tourney_name\n2026-900,Testville Open\n'
    calls = []

    def fake_get(url, **kw):
        calls.append(url.replace(tml.BASE_URL + '/', ''))
        if 'challenger' in url:
            return _Response(b'<html>Fehlerseite</html>')
        if 'quali' in url:
            return None  # 404
        return _Response(good)

    monkeypatch.setattr(tml, 'http_get', fake_get)
    loaded = tml.download([2026], tour='atp', levels=('main', 'challenger'))
    assert calls == ['2026.csv', 'ongoing_tourneys.csv', 'atp_quali/2026_atp_quali.csv', '2026_challenger.csv',
                     'challenger_ongoing_tourneys.csv']
    assert loaded == [('main', 2026), ('main', 'ongoing')]
    assert sorted(os.listdir(tmp_path)) == ['2026.csv', 'ongoing_tourneys.csv']  # keine Fehlerseite gespeichert

    # Frische Dateien werden nicht neu geladen, alte schon; ein Fehler lässt die alte Datei stehen
    calls.clear()
    tml.download([2026], tour='atp', levels=('main',), ongoing=False)
    assert calls == ['atp_quali/2026_atp_quali.csv']
    old = time.time() - 30 * 3600
    os.utime(tml.path(2026), (old, old))
    monkeypatch.setattr(tml, 'http_get', lambda url, **kw: _Response(b'<html>kaputt</html>'))
    assert tml.download([2026], tour='atp', levels=('main',), ongoing=False) == []
    assert open(tml.path(2026), 'rb').read() == good
    # WTA hat nur die Haupttour
    assert tml.kinds(('main', 'challenger', 'itf'), 'wta') == ['main']


def _sack(w, l, day, name='Roland Garros', **kw):
    return {'tour': 'atp', 'level': 'main', 'tourney_id': f'S-{name}', 'tourney_name': name, 'surface': 'Clay',
            'tourney_level': 'G', 'tourney_date': day, 'match_date': day, 'match_num': 1, 'round': 'R32',
            'winner_name': w, 'loser_name': l, 'score': '6-1 6-1', 'status': 'completed', 'source': 'sackmann', **kw}


def _other(source, w, l, day, name, **kw):
    return {'tour': 'atp', 'level': 'main', 'tourney_id': f'{source}-x', 'tourney_name': name, 'tourney_date': day,
            'match_date': day, 'match_num': 0, 'round': '', 'best_of': 3, 'winner_name': w, 'loser_name': l,
            'score': '', 'status': 'completed', 'source': source, **kw}


def test_build_uses_tml_after_sackmann(tmp_path, monkeypatch):
    monkeypatch.setattr(tml, 'DIR', _files(tmp_path))
    tml_rows = tml.load([2026], tour='atp', levels=('main', 'challenger'))
    # Vor dem Sackmann-Ende: dasselbe Match wie bei Sackmann (dort ohne Stats) und eins, das Sackmann nicht kennt
    _write(os.path.join(str(tmp_path), '2025.csv'), [
        _line('2026-520', 'Roland Garros', 'G', '20260528', 'Nia Xi', 'Oda Omikron', 'R32', surface='Clay'),
        _line('2026-520', 'Roland Garros', 'G', '20260526', 'Pam Pi', 'Rae Rho', 'R64', surface='Clay'),
    ])
    tml_rows += tml.load([2025], tour='atp', levels=('main',))

    sack = [_sack('Nia Xi', 'Oda Omikron', '20260525'), _sack('Sam Sigma', 'Tom Tau', '20260601', name='Stuttgart')]
    tuk_rows = [_other('tuk', 'Alpha A.', 'Beta B.', '20260914', 'Testville', B365W=1.5, B365L=2.6, PSW=1.55,
                       PSL=2.6, location='Testville')]
    espn_rows = [
        _other('espn', 'Ann Alpha', 'Cid Gamma', '20260917', 'Testville Open'),   # Zeitzone: einen Tag später
        _other('espn', 'Uma Ypsilon', 'Vic Phi', '20260919', 'Testville Open'),   # nur bei ESPN
    ]
    markets = [_other('kalshi', 'Hal Theta', 'Jon Kappa', '20260924', 'Lima', level='challenger', tourney_level='C')]
    players = {'atp': [{'player_id': '1', 'name': 'Ann Alpha', 'hand': 'L', 'dob': '19990101', 'ioc': 'GER'}]}

    rows, stats = build.build(sack, tuk_rows, espn_rows, players, markets, tml_rows)
    by = {(r['winner_name'], r['loser_name']): r for r in rows}

    # Sackmann hat Vorrang, bekommt aber Stats, Matchdatum und Halle/Freiluft aus TennisMyLife
    rg = by[('Nia Xi', 'Oda Omikron')]
    assert (rg['source'], rg['w_svpt'], rg['match_date'], rg['court']) == ('sackmann', '70', '20260528', 'Outdoor')
    assert stats['tml_stats_filled'] == 1
    assert ('Pam Pi', 'Rae Rho') not in by  # vor dem Sackmann-Ende und dort unbekannt: verworfen

    # Nach dem Sackmann-Ende: TennisMyLife ist die Quelle, tennis-data liefert die Quoten, ESPN nur noch Neues
    first = by[('Ann Alpha', 'Bea Beta')]
    assert (first['source'], first['B365W'], first['PSL'], first['w_ace']) == ('tml', 1.5, 2.6, '7')
    assert by[('Ann Alpha', 'Cid Gamma')]['source'] == 'tml'
    only_espn = by[('Uma Ypsilon', 'Vic Phi')]
    assert (only_espn['source'], only_espn['surface']) == ('espn', 'Hard')  # Untergrund aus dem TML-Turnier
    assert sum(r['source'] == 'espn' for r in rows) == 1
    assert stats['tml'] == 7 and stats['tuk'] == 0 and stats['espn'] == 1

    # Challenger: nur der Turnierstart bekannt, das Matchdatum kommt vom Markt, der Markt selbst fällt als Duplikat weg
    ch = by[('Hal Theta', 'Jon Kappa')]
    assert (ch['source'], ch['level'], ch['tourney_date'], ch['match_date']) == ('tml', 'challenger', '20260921',
                                                                                  '20260924')
    assert stats['kalshi_duplicates'] == 1 and not any(r['source'] == 'kalshi' for r in rows)

    # Spielerdaten: aus der Spielerliste, sonst Hand/Land der Zeile und das genäherte Geburtsdatum
    assert (first['winner_hand'], first['winner_ioc'], first['winner_dob']) == ('L', 'GER', '19990101')
    assert (first['loser_hand'], first['loser_ioc']) == ('L', 'BBB') and first['loser_dob'].startswith('1996')
    assert first['court'] == 'Outdoor' and by[('Ann Alpha', 'Cid Gamma')]['court'] == 'Indoor'


def test_window_for_start_date_only_rows():
    exact = {'source': 'tml', 'tourney_date': '20260912', 'match_date': '20260916'}
    start_only = {'source': 'tml', 'tourney_date': '20260921', 'match_date': '20260921'}
    lo, hi = build._window(exact)
    assert (hi - lo).days == 4
    lo, hi = build._window(start_only)
    assert (hi - lo).days == 17
    assert not build._start_date_only({'source': 'espn', 'tourney_date': '20260921', 'match_date': '20260921'})
    # Qualifikation: Datum = Start des Hauptfelds, gespielt in der Woche davor
    quali = {'source': 'tml', 'tourney_date': '20260629', 'match_date': '20260629', 'round': 'Q1'}
    lo, hi = build._window(quali)
    assert lo <= build._date('20260620') and hi >= build._date('20260629')


def test_build_matches_quali_market_a_week_before_main_draw():
    tml_rows = [{'tour': 'atp', 'level': 'main', 'tourney_id': 'tml-2026-540', 'tourney_name': 'Wimbledon',
                 'surface': 'Grass', 'tourney_level': 'G', 'tourney_date': '20260629', 'match_date': '20260629',
                 'match_num': 1, 'round': 'Q1', 'winner_name': 'Ann Alpha', 'loser_name': 'Bea Beta',
                 'score': '6-4 6-4', 'status': 'completed', 'source': 'tml', 'w_svpt': '60'}]
    sack = [_sack('Cid Gamma', 'Dan Delta', '20260525')]
    mk = [_other('kalshi', 'Ann Alpha', 'Bea Beta', '20260622', 'Wimbledon Men Singles')]
    rows, stats = build.build(sack, [], [], None, mk, tml_rows)
    assert [r['source'] for r in rows if r['winner_name'] == 'Ann Alpha'] == ['tml']
    assert stats['kalshi_duplicates'] == 1
