import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics
from utils import *

occ_ids = [3, 4, 9, 10, 12, 13, 18, 19, 20]
reg_ids = [5, 13]
pro_ids = [1, 2, 6, 7, 8, 11, 12, 14, 15, 16, 17]
split_ids = [12, 13]

acc_times_occ, exp_times_occ, acc_times_reg, exp_times_reg, acc_times_pro, exp_times_pro = [], [], [], [], [], []

#P12 - Professional + Occasional 
#P13 - Regular + Occasional 

# Occasional Users
for i in occ_ids:
    if i not in split_ids:
        codes = process_input(i)
        acc_times_occ.append(round(time_spent("acceleration", codes), 2))
        exp_times_occ.append(round(time_spent("exploration", codes), 2))
    else:
        all_times = times_split(i)
        acc_times_occ.append(all_times[2])
        exp_times_occ.append(all_times[3])

# Regular Users
for i in reg_ids:
    if i not in split_ids:
        codes = process_input(i)
        acc_times_reg.append(round(time_spent("acceleration", codes), 2))
        exp_times_reg.append(round(time_spent("exploration", codes), 2))
    else:
        all_times = times_split(i)
        acc_times_reg.append(all_times[0])
        exp_times_reg.append(all_times[1])

# Professional Users
for i in pro_ids:
    if i not in split_ids:
        codes = process_input(i)
        acc_times_pro.append(round(time_spent("acceleration", codes), 2))
        exp_times_pro.append(round(time_spent("exploration", codes), 2))
    else:
        all_times = times_split(i)
        acc_times_pro.append(all_times[0])
        exp_times_pro.append(all_times[1])

labels = ['Occasional\n(n=9)', 'Regular\n(n=2)', 'Professional\n(n=11)']

print("Median time spent in acceleration by occasional users", statistics.median(acc_times_occ))
print("Median time spent in exploration by occasional users", statistics.median(exp_times_occ))

print("Median time spent in acceleration by regular users", statistics.median(acc_times_reg))
print("Median time spent in exploration by regular users", statistics.median(exp_times_reg))

print("Median time spent in acceleration by professional users", statistics.median(acc_times_pro))
print("Median time spent in exploration by professional users", statistics.median(exp_times_pro))

acc = np.array([statistics.median(acc_times_occ), statistics.median(acc_times_reg), statistics.median(acc_times_pro)])
exp = np.array([statistics.median(exp_times_occ), statistics.median(exp_times_reg), statistics.median(exp_times_pro)])

width = 0.35

fig, ax = plt.subplots()

ax.bar(labels, acc, width, label='Acceleration', color="#00FFFF")
ax.bar(labels, exp, width, bottom=acc,
       label='Exploration', color="#FA8072")

ax.set_ylabel('Median time spent in each interaction mode (min)')
ax.set_title('Interaction modes based on participant\'s expertise')
ax.legend(loc='upper center')
plt.savefig('modes-expertise.pdf')