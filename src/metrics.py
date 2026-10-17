"""Explicit event definitions and scoring, independent of input/output."""
from bisect import bisect_left, bisect_right
from collections import Counter
import math

ROLES = {1:'GK', 2:'FB', 3:'CB', 4:'CB', 5:'CB', 6:'FB', 7:'FB', 8:'FB',
         9:'DM', 10:'DM', 11:'DM', 12:'W', 13:'CM', 14:'CM', 15:'CM',
         16:'W', 17:'W', 18:'AM', 19:'AM', 20:'AM', 21:'W',
         22:'ST', 23:'ST', 24:'ST', 25:'ST'}
COUNTS = ['passes_attempted','passes_completed','passes_excluded','progressive_passes',
          'final_third_passes','key_passes','assists','xg_assisted','shots','shots_on_target',
          'goals','non_penalty_goals','xg','npxg','dribbles_attempted','dribbles_completed',
          'progressive_carries','tackles_attempted','tackles_won','interceptions','recoveries',
          'pressures','aerial_wins','clearances','blocks','dribbled_past','dispossessed',
          'miscontrols','box_touches','fouls_committed']
COUNTS += ['key_passes_open_play','key_passes_set_piece','xg_assisted_open_play','xg_assisted_set_piece']
MAX_SLOTS = 8
LABELS = {
    'passes_attempted':'Pases evaluables', 'passes_completed':'Pases completados',
    'progressive_passes':'Pases progresivos completados', 'final_third_passes':'Pases completados al último tercio',
    'key_passes':'Pases que generan tiro', 'assists':'Asistencias', 'xg_assisted':'xG de tiros asistidos',
    'shots':'Tiros', 'shots_on_target':'Tiros a puerta', 'goals':'Goles',
    'non_penalty_goals':'Goles sin penaltis', 'xg':'xG', 'npxg':'xG sin penaltis',
    'dribbles_attempted':'Regates intentados', 'dribbles_completed':'Regates completados',
    'progressive_carries':'Conducciones progresivas', 'tackles_attempted':'Entradas intentadas',
    'tackles_won':'Entradas ganadas', 'interceptions':'Intercepciones exitosas',
    'recoveries':'Recuperaciones exitosas', 'pressures':'Presiones', 'aerial_wins':'Duelos aéreos ganados',
    'clearances':'Despejes', 'blocks':'Bloqueos', 'dribbled_past':'Veces superado por regate',
    'dispossessed':'Desposesiones sufridas', 'miscontrols':'Malos controles',
    'box_touches':'Recepciones y tiros en el área', 'fouls_committed':'Faltas cometidas'}
NEGATIVE = {'dribbled_past_p90','dispossessed_p90','miscontrols_p90','fouls_committed_p90'}
LABELS.update({'key_passes_open_play':'Pases que generan tiro en juego abierto',
               'key_passes_set_piece':'Pases que generan tiro a balón parado',
               'xg_assisted_open_play':'xG de tiros asistidos en juego abierto',
               'xg_assisted_set_piece':'xG de tiros asistidos a balón parado'})


def creation_context(event):
    """Corner/FK phases plus direct restarts; remaining passing creation is open play.

    Throw-in/goal-kick/kick-off phases are not wholly set pieces: only the
    restart itself, if it directly assists a shot. This is a versioned proxy.
    """
    direct = event.get('pass', {}).get('type', {}).get('name')
    pattern = event.get('play_pattern', {}).get('name')
    if direct in {'Corner','Free Kick','Throw-in','Goal Kick','Kick Off'} or pattern in {'From Corner','From Free Kick'}:
        return 'set_piece'
    return 'open_play'


def clock_minutes(value):
    parts = [float(x) for x in value.split(':')]
    return parts[0] * 60 + parts[1] + parts[2] / 60 if len(parts) == 3 else parts[0] + parts[1] / 60


def regulation_time(value, period):
    """Lineup clocks are match clocks. Remove added time separately per period."""
    start = {1:0, 2:45, 3:90, 4:105}[period]
    length = 45 if period <= 2 else 15
    return start + min(length, max(0, clock_minutes(value) - start))


def stint_minutes(stint):
    start = regulation_time(stint['from'], stint['from_period'])
    end = regulation_time(stint['to'], stint['to_period']) if stint['to'] is not None else 90
    if end < start:
        raise ValueError(f'Negative stint: {stint}')
    return end - start


def progressive(start, end):
    if not start or not end:
        return False
    before = math.hypot(120 - start[0], 40 - start[1])
    after = math.hypot(120 - end[0], 40 - end[1])
    return end[0] >= 60 and before - after >= 10 and after <= .75 * before


def event_counts(event, shots_by_id):
    c = Counter()
    kind = event['type']['name']
    if kind == 'Pass':
        p = event['pass']
        outcome = p.get('outcome', {}).get('name', 'Complete')
        if outcome in {'Unknown','Injury Clearance'}:
            c['passes_excluded'] = 1
        else:
            c['passes_attempted'] = 1
        if outcome == 'Complete':
            c['passes_completed'] = 1
            open_play = p.get('type', {}).get('name') not in {'Corner','Free Kick','Throw-in','Kick Off','Goal Kick'}
            c['progressive_passes'] = int(open_play and progressive(event.get('location'), p.get('end_location')))
            loc, end = event.get('location'), p.get('end_location')
            c['final_third_passes'] = int(bool(open_play and loc and end and loc[0] < 80 <= end[0]))
        assisted = shots_by_id.get(p.get('assisted_shot_id'))
        c['key_passes'] = int(bool(p.get('shot_assist') or p.get('goal_assist') or assisted))
        c['assists'] = int(bool(p.get('goal_assist')))
        if c['key_passes']:
            context = creation_context(event)
            c['key_passes_' + context] = 1
            if not assisted:
                raise ValueError('Creation event without linked shot: cannot assign assisted xG')
        if assisted:
            c['xg_assisted'] = assisted['shot']['statsbomb_xg']
            c['xg_assisted_' + context] = c['xg_assisted']
    elif kind == 'Shot':
        s = event['shot']
        c['shots'] = 1
        goal = s['outcome']['name'] == 'Goal'
        c['goals'] = int(goal)
        c['shots_on_target'] = int(s['outcome']['name'] in {'Goal','Saved','Saved to Post'})
        c['xg'] = s['statsbomb_xg']
        if s.get('type', {}).get('name') != 'Penalty':
            c['non_penalty_goals'] = int(goal)
            c['npxg'] = c['xg']
    elif kind == 'Dribble':
        c['dribbles_attempted'] = 1
        c['dribbles_completed'] = int(event['dribble']['outcome']['name'] == 'Complete')
    elif kind == 'Carry':
        c['progressive_carries'] = int(progressive(event.get('location'), event['carry'].get('end_location')))
    elif kind == 'Duel' and event['duel'].get('type', {}).get('name') == 'Tackle':
        c['tackles_attempted'] = 1
        c['tackles_won'] = int(event['duel'].get('outcome', {}).get('name') in {'Won','Success','Success In Play','Success Out'})
    elif kind == 'Interception':
        c['interceptions'] = int(event['interception']['outcome']['name'] in {'Won','Success','Success In Play','Success Out'})
    elif kind == 'Ball Recovery':
        c['recoveries'] = int(not event.get('ball_recovery', {}).get('recovery_failure', False))
    else:
        name = {'Pressure':'pressures','Clearance':'clearances','Block':'blocks',
                'Dribbled Past':'dribbled_past','Dispossessed':'dispossessed',
                'Miscontrol':'miscontrols','Foul Committed':'fouls_committed'}.get(kind)
        if name:
            c[name] = 1
    # StatsBomb attaches aerial_won to several event subtypes, count once per event.
    c['aerial_wins'] = int(any(isinstance(v, dict) and v.get('aerial_won') for v in event.values()))
    loc = event.get('location')
    received = kind == 'Ball Receipt*' and 'outcome' not in event.get('ball_receipt', {})
    if (received or kind == 'Shot') and loc and loc[0] >= 102 and 18 <= loc[1] <= 62:
        c['box_touches'] = 1
    return c


def rates(counts, minutes):
    out = {k + '_p90': counts.get(k, 0) * 90 / minutes if minutes > 0 else None
           for k in LABELS}
    for name, num, den in [('pass_completion_pct','passes_completed','passes_attempted'),
                           ('dribble_success_pct','dribbles_completed','dribbles_attempted'),
                           ('tackle_success_pct','tackles_won','tackles_attempted')]:
        out[name] = 100 * counts.get(num, 0) / counts[den] if counts.get(den, 0) > 0 else None
    return out


def percentile(value, population, negative=False):
    """Midrank ECDF: ties share percentile; constant population gets 50."""
    if value is None or not population:
        return None
    values = sorted(population)
    p = 100 * (bisect_left(values, value) + bisect_right(values, value)) / (2 * len(values))
    return 100 - p if negative else p


def score(values, weights):
    active = {k:v for k,v in weights.items() if v > 0}
    if any(not math.isfinite(v) or v < 0 for v in weights.values()):
        raise ValueError('Weights must be finite and non-negative')
    if not active or any(values.get(k) is None for k in active):
        return None
    # Stabilize mathematically identical sums across Python, JS and DAX.
    return round(sum(values[k] * w for k,w in active.items()) / sum(active.values()), 8)
