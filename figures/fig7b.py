import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics
from utils import *

ids = [7, 8, 1, 6, 4, 2, 3, 5, 10, 9, 11, 12, 13, 14, 16, 18, 19, 20, 15, 17]
acc_examine_times, acc_run_times, acc_api_times = [], [], []
exp_examine_times, exp_run_times, exp_api_times = [], [], []

acc_times, exp_times = [], []
total_times = []

for i in ids:
    codes = process_input(i)
    acc_times.append(round(time_spent("acceleration", codes), 2))
    exp_times.append(round(time_spent("exploration", codes), 2))
    total_times.append(round(get_total_time(codes), 2))

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

total_api_times = [round(x[0] + x[1], 2) for x in zip(acc_api_times, exp_api_times)]
total_examine_times = [round(x[0] + x[1], 2) for x in zip(acc_examine_times, exp_examine_times)]
total_run_times = [round(x[0] + x[1], 2) for x in zip(acc_run_times, exp_run_times)]
times = list(zip(acc_times, exp_times, total_times))
interact_times = [(round((a[0] + a[1])/a[2] * 100,2)) for a in times]

examine_task1 = [x[0] for x in zip(total_examine_times[0:5], interact_times[0:5])]
examine_task2 = [x[0] for x in zip(total_examine_times[5:9], interact_times[5:9])]
examine_task3 = [x[0] for x in zip(total_examine_times[9:13], interact_times[9:13])]
examine_task4 = [x[0] for x in zip(total_examine_times[13:20], interact_times[13:20])]

print('Chat Server-Examination', np.median(examine_task1))
print('Chat Client-Examination', np.median(examine_task2))
print('Benford Law-Examination', np.median(examine_task3))
print('Advent of Code-Examination', np.median(examine_task4))

run_task1 = [x[0] for x in zip(total_run_times[0:5], interact_times[0:5])]
run_task2 = [x[0] for x in zip(total_run_times[5:9], interact_times[5:9])]
run_task3 = [x[0] for x in zip(total_run_times[9:13], interact_times[9:13])]
run_task4 = [x[0] for x in zip(total_run_times[13:20], interact_times[13:20])]

print('Chat Server-Execution', np.median(run_task1))
print('Chat Client-Execution', np.median(run_task2))
print('Benford Law-Execution', np.median(run_task3))
print('Advent of Code-Execution', np.median(run_task4))

api_task1 = [x[0] for x in zip(total_api_times[0:5], interact_times[0:5])]
api_task2 = [x[0] for x in zip(total_api_times[5:9], interact_times[5:9])]
api_task3 = [x[0] for x in zip(total_api_times[9:13], interact_times[9:13])]
api_task4 = [x[0] for x in zip(total_api_times[13:20], interact_times[13:20])]

print('Chat Server-Documentation', np.median(api_task1))
print('Chat Client-Documentation', np.median(api_task2))
print('Benford Law-Documentation', np.median(api_task3))
print('Advent of Code-Documentation', np.median(api_task4))

labels = ['Chat Server\n(n=5)', 'Chat Client\n(n=4)', 'Benford\'s law\n(n=4)', 'Advent of Code\n(n=7)']

api = np.array([np.median(api_task1), np.median(api_task2), np.median(api_task3), np.median(api_task4)])
run = np.array([np.median(run_task1), np.median(run_task2), np.median(run_task3), np.median(run_task4)])
examine = np.array([np.median(examine_task1), np.median(examine_task2), np.median(examine_task3), np.median(examine_task4)])

width = 0.25 # the width of the bars: can also be len(x) sequence

fig, ax = plt.subplots()

ax.bar(labels, examine, width, label='Examination', color="#00FFFF")
ax.bar(labels, run, width, bottom=examine,
       label='Execution', color='y')
ax.bar(labels, api, width, bottom=run+examine,
       label='Documentation', color="g")

ax.set_ylabel('Median time spent in each validation technique', fontsize=10)
ax.set_title('Validation techniques grouped by Task (n = participants)', fontsize=10)
ax.legend()

plt.savefig('val-task.pdf')