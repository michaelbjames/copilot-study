import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics
from utils import *

nopcu_ids = [2, 3, 5, 7, 8, 9, 10, 14, 16, 18, 19]
pcu_ids = [1, 4, 6, 11, 12, 13, 15, 17, 20]

acc_times_pcu = []
exp_times_pcu = []
acc_times_nopcu = []
exp_times_nopcu = []

for i in nopcu_ids:
    codes = process_input(i)
    acc_times_nopcu.append(round(time_spent("acceleration", codes), 2))
    exp_times_nopcu.append(round(time_spent("exploration", codes), 2))

for i in pcu_ids:
    codes = process_input(i)
    acc_times_pcu.append(round(time_spent("acceleration", codes), 2))
    exp_times_pcu.append(round(time_spent("exploration", codes), 2)) 

print("Median time for acceleration in No-PCU users", statistics.median(acc_times_nopcu))
print("Median time for exploration in No-PCU users", statistics.median(exp_times_nopcu))

print("Median time for acceleration in PCU users", statistics.median(acc_times_pcu))
print("Median time for exploration in PCU users", statistics.median(exp_times_pcu))

labels = ['PCU (n=9)', 'No-PCU (n=11)']

acc = np.array([statistics.median(acc_times_pcu), statistics.median(acc_times_nopcu)])
exp = np.array([statistics.median(exp_times_pcu), statistics.median(exp_times_nopcu)])

width = 0.20

fig, ax = plt.subplots()

ax.bar(labels, acc, width, label='Acceleration', color="#00FFFF")
ax.bar(labels, exp, width, bottom=acc,
       label='Exploration', color="#FA8072")

ax.set_ylabel('Median time spent in each interaction mode (min)')
ax.set_title('Interaction modes based on participant\'s Prior Copilot Usage (PCU)', fontsize=10)
ax.legend(loc='upper center')
plt.savefig('modes-pcu.pdf')