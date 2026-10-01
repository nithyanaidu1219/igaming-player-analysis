"""Rebuild the synthetic SQLite dataset and SQL outputs. Python standard library only."""
from pathlib import Path
import sqlite3, random, datetime as dt
root = Path(__file__).resolve().parent
rng = random.Random(42)
db = root / 'data/igaming.db'
db.unlink(missing_ok=True)
c = sqlite3.connect(db)
c.executescript('''
PRAGMA foreign_keys=ON;
CREATE TABLE players(player_id INTEGER PRIMARY KEY, registration_date TEXT NOT NULL, channel TEXT NOT NULL);
CREATE TABLE deposits(deposit_id INTEGER PRIMARY KEY, player_id INTEGER REFERENCES players, deposit_date TEXT NOT NULL, amount_cents INTEGER CHECK(amount_cents>0));
CREATE TABLE player_daily(player_id INTEGER REFERENCES players, activity_date TEXT NOT NULL, rounds INTEGER CHECK(rounds>0), stakes_cents INTEGER CHECK(stakes_cents>0), payouts_cents INTEGER CHECK(payouts_cents>=0), PRIMARY KEY(player_id, activity_date));
''')
start, end = dt.date(2026, 7, 1), dt.date(2026, 9, 30)
for pid in range(1, 501):
    reg = start + dt.timedelta(days=rng.randrange(92))
    c.execute('INSERT INTO players VALUES(?,?,?)', (pid, str(reg), rng.choice(['Organic', 'Paid search', 'Affiliate'])))
    if rng.random() > .64:
        continue
    first = reg + dt.timedelta(days=rng.randrange(15))
    balance = 0
    propensity = rng.uniform(.08, .35)
    unit = rng.choice([100, 200, 500, 1000])
    day = first
    while day <= end:
        if day == first or (balance < unit * 10 and rng.random() < .18):
            amount = rng.choice([5000, 10000, 20000])
            c.execute('INSERT INTO deposits(player_id,deposit_date,amount_cents) VALUES(?,?,?)', (pid, str(day), amount))
            balance += amount
        if rng.random() < propensity and balance >= unit:
            rounds = stakes = payouts = 0
            for _ in range(rng.randint(5, 45)):
                if balance < unit:
                    break
                # Stylised game: 45% chance of returning twice the stake; no real operator model.
                payout = 2 * unit if rng.random() < .45 else 0
                balance += payout - unit
                rounds += 1
                stakes += unit
                payouts += payout
            c.execute('INSERT INTO player_daily VALUES(?,?,?,?,?)', (pid, str(day), rounds, stakes, payouts))
        day += dt.timedelta(days=1)
c.commit()
assert c.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
assert not c.execute('PRAGMA foreign_key_check').fetchall()
assert c.execute('SELECT COUNT(*) FROM player_daily a JOIN players p USING(player_id) WHERE activity_date<registration_date').fetchone()[0] == 0
# Independent totals make accidental join inflation visible.
expected = c.execute('SELECT SUM(stakes_cents),SUM(payouts_cents) FROM player_daily').fetchone()
for query in sorted((root/'sql').glob('*.sql')):
    cur = c.execute(query.read_text())
    headers = [d[0] for d in cur.description]
    rows = cur.fetchall()
    if query.name.startswith('01'):
        assert round(sum(r[5] for r in rows)*100) == expected[0]
        assert round(sum(r[6] for r in rows)*100) == expected[1]
    text = '| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join(['---']*len(headers)) + ' |\n'
    text += '\n'.join('| ' + ' | '.join(str(v) for v in row) + ' |' for row in rows)
    (root/'results'/f'{query.stem}.md').write_text(text+'\n')
print('Validated 500 players; activity rows:', c.execute('SELECT COUNT(*) FROM player_daily').fetchone()[0])
c.close()
