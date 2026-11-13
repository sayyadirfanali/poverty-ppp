"""Goods share of spending by fractile, from HCES 2022-23 Table A6 (All-India)."""
import openpyxl, sys

GOODS = ['Food: Total', 'Pan, Tobacco & Intoxicants', 'Fuel and light', 'Toilet articles',
         'Other household consumables', 'Clothing & bedding', 'Footwear', 'Durable goods']
SERVICES = ['Education', 'Consumer services excluding conveyance', 'Rent', 'Other taxes & cesses']
# mixed groups: (name, goods fraction in central case)
MIXED = [('Medical (Non-Hospitalization)', 2/3),   # mostly medicines
         ('Medical (Hospitalization)', 0.0),
         ('Conveyance', 0.5),                       # vehicle fuel vs fares
         ('Entertainment', 0.0)]

def load(path):
    ws = openpyxl.load_workbook(path, data_only=True).active
    out, sec, st = {}, None, None
    for r in ws.iter_rows(values_only=True):
        if r[0] in ('Rural', 'Urban'): sec = r[0]
        if r[1]: st = r[1]
        if st and 'india' in str(st).lower() and r[2] and isinstance(r[3], (int, float)):
            out[(sec, r[2])] = dict(b5=r[3], b10=(r[3] + r[4]) / 2, all=r[15])
    return out

def shares(d, sec, col):
    g = sum(d[(sec, k)][col] for k in GOODS)
    s = sum(d[(sec, k)][col] for k in SERVICES)
    m = [(d[(sec, k)][col], f) for k, f in MIXED]
    tot = d[(sec, 'Total Expenditure')][col]
    mixed = sum(v for v, _ in m)
    assert abs(g + s + mixed - tot) / tot < 0.01, (sec, col, g + s + mixed, tot)
    return dict(low=g / tot, mid=(g + sum(v * f for v, f in m)) / tot, high=(g + mixed) / tot)

if __name__ == '__main__':
    d = load(sys.argv[1] if len(sys.argv) > 1 else './Table_A6.xlsx')
    for sec in ('Rural', 'Urban'):
        for col, name in (('b5', 'bottom 5%'), ('b10', 'bottom 10%'), ('all', 'everyone')):
            x = shares(d, sec, col)
            print(f"{sec:5s} {name:10s} goods share at Indian prices: "
                  f"low {x['low']:.3f}  central {x['mid']:.3f}  high {x['high']:.3f}")
