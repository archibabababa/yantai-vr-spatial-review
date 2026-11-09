"""Reproduce simultaneous high ratings on Q10 (circulation) and Q11 (display)."""
import csv
from pathlib import Path


def load(path):
    with path.open(encoding='utf-8-sig', newline='') as source:
        return list(csv.DictReader(source))


def bounds(row):
    if row['status'] == 'point':
        return (int(row['score']),) * 2
    if row['status'] == 'interval':
        return int(row['lower']), int(row['upper'])
    assert row['status'] == 'unresolved'
    return 1, 5


def calculate(folder):
    responses = load(folder/'Anonymous participant ratings.csv')
    pairs = {(r['participant'],r['item']): bounds(r) for r in responses if r['item'] in ('Q10','Q11')}
    results = []
    for group in ['Students','Experts']:
        people = {r['participant'] for r in responses if r['group'] == group}
        assert len(people) == 15
        joint = [tuple(min(a,b) for a,b in zip(pairs[p,'Q10'],pairs[p,'Q11'])) for p in people]
        results.append([group,len(people),'Within-person thresholds',
                        sum(lo >= 4 for lo,_ in joint),sum(hi >= 4 for _,hi in joint)])
    alternative = {r['item']:r for r in load(folder/'Expert rating sensitivity by item.csv')}
    a, b = (int(alternative[q]['high']) for q in ('10','11'))
    n = int(alternative['10']['n'])
    assert n == int(alternative['11']['n']) == 15
    # Sharp overlap bounds from the two available marginal totals.
    results.append(['Experts (alternative tabulation)',n,'Bounds from item totals',max(0,a+b-n),min(a,b)])
    with (folder/'Joint circulation and display ratings.csv').open('w',encoding='utf-8',newline='') as stream:
        out = csv.writer(stream)
        out.writerow(['group','participants','basis','both_high_lower','both_high_upper'])
        out.writerows(results)
    return results


if __name__ == '__main__':
    calculate(Path(__file__).resolve().parent)
