import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics
from utils import *

task1_ids = [1, 4, 6, 7, 8]
task2_ids = [2, 3, 5, 10]
task3_ids = [9, 11, 12, 13]
task4_ids = [14, 15, 16, 17, 18, 19, 20]

acc_times_task1 = []
exp_times_task1 = []
acc_times_task2 = []
exp_times_task2 = []
acc_times_task3 = []
exp_times_task3 = []
acc_times_task4 = []
exp_times_task4 = []

for i in task1_ids:
    codes = process_input(i)
    acc_times_task1.append(round(time_spent("acceleration", codes), 2))
    exp_times_task1.append(round(time_spent("exploration", codes), 2))

for i in task2_ids:
    codes = process_input(i)
    acc_times_task2.append(round(time_spent("acceleration", codes), 2))
    exp_times_task2.append(round(time_spent("exploration", codes), 2)) 

for i in task3_ids:
    codes = process_input(i)
    acc_times_task3.append(round(time_spent("acceleration", codes), 2))
    exp_times_task3.append(round(time_spent("exploration", codes), 2))

for i in task4_ids:
    codes = process_input(i)
    acc_times_task4.append(round(time_spent("acceleration", codes), 2))
    exp_times_task4.append(round(time_spent("exploration", codes), 2)) 

print("Median time for acceleration in Chat Server", statistics.median(acc_times_task1))
print("Median time for exploration in Chat Server", statistics.median(exp_times_task1))

print("Median time for acceleration in Chat Client", statistics.median(acc_times_task2))
print("Median time for exploration in Chat Client", statistics.median(exp_times_task2))

print("Median time for acceleration in Benford's law", statistics.median(acc_times_task3))
print("Median time for exploration in Benford's law", statistics.median(exp_times_task3))

print("Median time for acceleration in Advent of Code", statistics.median(acc_times_task4))
print("Median time for exploration in Advent of Code", statistics.median(exp_times_task4))

labels = ['Chat Server\n(n=5)', 'Chat Client\n(n=4)', 'Benford\'s law\n(n=4)', 'Advent of Code\n(n=7)']

acc = np.array([statistics.median(acc_times_task1), statistics.median(acc_times_task2), statistics.median(acc_times_task3), statistics.median(acc_times_task4)])
exp = np.array([statistics.median(exp_times_task1), statistics.median(exp_times_task2), statistics.median(exp_times_task3), statistics.median(exp_times_task4)])

width = 0.35

fig, ax = plt.subplots()

ax.bar(labels, acc, width, label='Acceleration', color="#00FFFF")
ax.bar(labels, exp, width, bottom=acc,
       label='Exploration', color="#FA8072")

ax.set_ylabel('Median time spent in each interaction mode (min)', fontsize=11)
ax.set_title('Interaction modes grouped by Task (n = participants)', fontsize=11)
ax.legend(loc=(0.1, 0.8))
plt.savefig('modes-task.pdf')