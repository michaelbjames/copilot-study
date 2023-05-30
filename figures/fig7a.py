import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics
from utils import *

ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
acc_examine_times, acc_run_times, acc_api_times, exp_examine_times, exp_run_times, exp_api_times = [], [], [], [], [], []

for i in ids:
    codes = process_input(i)
    
    acc_examine = time_spent_validate("acc/validate/examine", codes)
    acc_examine_times.append(round(acc_examine,2))
    acc_api = time_spent_validate("acc/validate/api", codes) + time_spent_validate("acc/validate/IDE", codes)
    acc_api_times.append(round(acc_api,2))
    acc_run = time_spent_validate("acc/validate/run", codes)
    acc_run_times.append(round(acc_run,2))

    exp_examine = time_spent("exp/validate/examine/multi-menu", codes) + time_spent("exp/validate/inline", codes) +\
    time_spent("expl/validate/inline", codes) + time_spent("exp/examine/validate/inline", codes) +\
    time_spent("exp/validate/examine", codes) + time_spent("exp/validate/examine/inline", codes) +\
    time_spent("exp/validate/examine/exp/validate/examine/spec", codes) +\
    time_spent("exp/validate/examine/multi-line", codes)
    exp_examine_times.append(round(exp_examine,2))

    exp_run = time_spent_validate("exp/validate/run", codes) + time_spent("exp/validate/debugger", codes)
    exp_run_times.append(round(exp_run,2))

    exp_api = time_spent_validate("exp/validate/api", codes) + time_spent_validate("exp/validate/google", codes) +\
    time_spent("exp/validate/examine/api(in-ide)", codes) + time_spent("exp/validate/in-ide(errors)", codes)
    exp_api_times.append(round(exp_api,2))

acc_sum = sum(acc_examine_times) + sum(acc_run_times) + sum(acc_api_times)
acc_plot = [round(sum(acc_examine_times)/acc_sum * 100, 2), round(sum(acc_run_times)/acc_sum * 100, 2), round(sum(acc_api_times)/acc_sum * 100, 2)]

exp_sum = sum(exp_examine_times) + sum(exp_run_times) + sum(exp_api_times)
exp_plot = [round(sum(exp_examine_times)/exp_sum * 100, 2), round(sum(exp_run_times)/exp_sum * 100, 2), round(sum(exp_api_times)/exp_sum * 100, 2)]

print("Examination in acceleration mode", acc_plot[0])
print("Execution in acceleration mode", acc_plot[1])
print("Documentation in acceleration mode", acc_plot[2])

print("Examination in exploration mode", exp_plot[0])
print("Execution in exploration mode", exp_plot[1])
print("Documentation in exploration mode", exp_plot[2])

labels = ['Acceleration', 'Exploration']

examine = np.array([acc_plot[0], exp_plot[0]])
run = np.array([acc_plot[1], exp_plot[1]])
api = np.array([acc_plot[2], exp_plot[2]])

width = 0.2

fig, ax = plt.subplots()

ax.bar(labels, examine, width, label='Examination', color="#00FFFF")
ax.bar(labels, run, width, bottom=examine,
       label='Execution', color='y')
ax.bar(labels, api, width, bottom=run+examine,
       label='Documentation', color="g")

ax.set_ylabel('% Time spent in each validation strategy', fontsize=10)
ax.set_title('Validation strategies in the two interaction modes', fontsize=10)
ax.legend(loc='upper center')

plt.savefig('val-modes.pdf')