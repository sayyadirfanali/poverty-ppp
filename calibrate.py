from shares import load, GOODS, SERVICES

EXR = 73.92              # market rate 2021, rupees per US dollar (only used for price levels)
ICP_HH = 19.47           # ICP 2021 PPP, households and NPISHs final consumption
ICP_HH_NOHOUSING = 22.58 # ICP 2021 PPP, household consumption without housing

# ICP 2021 PPPs (rupees per US$) for the headings each HCES group is matched to
PPP = { 'food': 37.02,
        'tobacco': 34.20,
        'clothing': 22.24,
        'furnishings': 30.62,
        'misc': 21.79,
        'transport': 39.29,
        'transport_services': 29.96,
        'housing': 9.93,
        'health': 8.19,
        'education': 10.29,
        'restaurants': 20.37,
        'recreation': 27.15 }

# HCES group -> (goods fraction, heading for goods part, heading for services part)
GROUPS = {
 'Food: Total': (1, 'food', None),
 'Pan, Tobacco & Intoxicants': (1, 'tobacco', None),
 'Fuel and light': (1, 'transport', None),        # energy proxy, no clean heading
 'Toilet articles': (1, 'misc', None),
 'Other household consumables': (1, 'furnishings', None),
 'Clothing & bedding': (1, 'clothing', None),
 'Footwear': (1, 'clothing', None),
 'Durable goods': (1, 'furnishings', None),
 'Education': (0, None, 'education'),
 'Consumer services excluding conveyance': (0, None, 'restaurants'),
 'Rent': (0, None, 'housing'),
 'Other taxes & cesses': (0, None, 'misc'),
 'Medical (Non-Hospitalization)': (2/3, 'health', 'health'),   # mostly medicines
 'Medical (Hospitalization)': (0, 'health', 'health'),
 'Conveyance': (0.5, 'transport', 'transport_services'),       # vehicle fuel vs fares
 'Entertainment': (0, 'recreation', 'recreation'),
}
assert set(GROUPS) == set(GOODS) | set(SERVICES) | {
    'Medical (Non-Hospitalization)', 'Medical (Hospitalization)', 'Conveyance', 'Entertainment'}

def split(d, sec, col):
    """Spending on goods and services, each as a list of (rupees, PPP)."""
    g, s = [], []
    for k, (f, hg, hs) in GROUPS.items():
        v = d[(sec, k)][col]
        if f: g.append((v * f, PPP[hg]))
        if f < 1: s.append((v * (1 - f), PPP[hs]))
    return g, s

def ratio(parts):   # fixed-basket PPP of a set of spending: rupees / dollars
    return sum(v for v, _ in parts) / sum(v / r for v, r in parts)

def model(d, sec, col, rg=None, rs=None):
    g, s = split(d, sec, col)
    rg = rg or ratio(g); rs = rs or ratio(s)
    G, S = sum(v for v, _ in g), sum(v for v, _ in s)
    w = (G / rg) / (G / rg + S / rs)          # goods share at US prices
    return dict(rg=rg, rs=rs, w=w, ppp=rs + w * (rg - rs), share=G / (G + S))

if __name__ == '__main__':
    d = load('./Table_A6.xlsx')
    print(f"ICP household consumption PPP: {ICP_HH}  (price level {ICP_HH/EXR:.3f})")
    print(f"ICP household consumption PPP without housing: {ICP_HH_NOHOUSING}\n")
    # one pair of price ratios, from the average rural+urban basket
    ga, sa = [], []
    for sec in ('Rural', 'Urban'):
        g, s = split(d, sec, 'all'); ga += g; sa += s
    rg, rs = ratio(ga), ratio(sa)
    print(f"goods ratio {rg:.2f}  services ratio {rs:.2f}  (rupees per $)")
    for sec in ('Rural', 'Urban'):
        a = model(d, sec, 'all', rg, rs); p = model(d, sec, 'b10', rg, rs)
        print(f"  {sec:5s} avg: share {a['share']:.3f} w_US {a['w']:.3f} PPP {a['ppp']:.2f} | "
              f"bottom 10%: share {p['share']:.3f} w_US {p['w']:.3f} PPP {p['ppp']:.2f} | "
              f"gap {100*(p['ppp']/a['ppp']-1):.1f}%")
    # external check: our average basket vs ICP (HCES excludes imputed rent)
    for sec in ('Rural', 'Urban'):
        a = model(d, sec, 'all', rg, rs)
        print(f"  check {sec:5s}: our average-basket PPP {a['ppp']:.2f} vs ICP without housing "
              f"{ICP_HH_NOHOUSING} ({100*(a['ppp']/ICP_HH_NOHOUSING-1):+.1f}%)")
