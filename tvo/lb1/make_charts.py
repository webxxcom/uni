# Builds img/time.png and img/speedup.png from results/results.csv. Run: python make_charts.py
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CORES = 6  # фізичних ядер (Ryzen 5 5600), логічних 12

rows = list(csv.DictReader(open('results/results.csv', encoding='utf-8'), delimiter=';'))
p = [int(r['threads']) for r in rows]
t = [float(r['median_ms']) for r in rows]
s = [float(r['speedup']) for r in rows]
t1 = t[0]

plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 13})

fig, ax = plt.subplots(figsize=(7.5, 4.3), dpi=200)
ax.plot(p, t, 'o-', color='#1f4e9c', label='Експеримент (медіана)')
ax.plot(p, [t1 / x for x in p], '--', color='#888888', label='Теорія: T1/p')
ax.plot(p, [t1 / min(x, CORES) for x in p], ':', color='#c0392b', label=f'Теорія з урахуванням {CORES} ядер: T1/min(p, {CORES})')
ax.set_xlabel('Кількість потоків p')
ax.set_ylabel('Час обробки, мс')
ax.set_xticks(p)
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig('img/time.png')

fig, ax = plt.subplots(figsize=(7.5, 4.3), dpi=200)
ax.plot(p, s, 'o-', color='#1f4e9c', label='Експеримент')
ax.plot(p, p, '--', color='#888888', label='Ідеальне прискорення S = p')
ax.plot(p, [min(x, CORES) for x in p], ':', color='#c0392b', label=f'Межа за кількістю ядер: min(p, {CORES})')
ax.set_xlabel('Кількість потоків p')
ax.set_ylabel('Прискорення S')
ax.set_xticks(p)
ax.set_ylim(0, 9)
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig('img/speedup.png')
print('ok')
