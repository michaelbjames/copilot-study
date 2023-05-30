import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics
from utils import *

a_prompt = (0, 0, 0, 0)
e_prompt = (0, 0, 0, 0)
ids = [7, 8, 1, 6, 4, 2, 3, 5, 10, 9, 11, 12, 13, 14, 16, 18, 19, 20, 15, 17]

for i in ids:
    codes = process_input(i)
    for code in codes:
       if "acc/prompt/code" in code[2]:
           a_prompt = (a_prompt[0] + 1, a_prompt[1], a_prompt[2], a_prompt[3])
       elif "acc/prompt/nl" in code[2]:
           a_prompt = (a_prompt[0], a_prompt[1] + 1, a_prompt[2], a_prompt[3])
       elif "acc/prompt/multi-menu" in code[2]:
           a_prompt = (a_prompt[0], a_prompt[1], a_prompt[2] + 1, a_prompt[3])
       elif "acc/prompt/context" in code[2]:
           a_prompt = (a_prompt[0], a_prompt[1], a_prompt[2], a_prompt[3] + 1)

       elif "exp/prompt/code" in code[2]:
           e_prompt = (e_prompt[0] + 1, e_prompt[1], e_prompt[2], e_prompt[3])
       elif "exp/prompt/nl" in code[2]:
           e_prompt = (e_prompt[0], e_prompt[1] + 1, e_prompt[2], e_prompt[3])
       elif "exp/prompt/multi-menu" in code[2]:
           e_prompt = (e_prompt[0], e_prompt[1] + 1, e_prompt[2] + 1, e_prompt[3])
       elif "exp/prompt/context" in code[2]:
           e_prompt = (e_prompt[0], e_prompt[1] + 1, e_prompt[2], e_prompt[3] + 1)

print("Code Prompt in acceleration mode", a_prompt[0]/ sum(a_prompt) * 100)
print("Code Prompt in exploration mode", e_prompt[0]/ sum(e_prompt) * 100)

print("Context Prompt in acceleration mode", a_prompt[3]/ sum(a_prompt) * 100)
print("Context Prompt in exploration mode", e_prompt[3]/ sum(e_prompt) * 100)

print("Comment Prompt in acceleration mode", a_prompt[1]/ sum(a_prompt) * 100)
print("Comment Prompt in exploration mode", e_prompt[1]/ sum(e_prompt) * 100)

print("Pane Prompt in acceleration mode", a_prompt[2]/ sum(a_prompt) * 100)
print("Pane Prompt in exploration mode", e_prompt[2]/ sum(e_prompt) * 100)

labels = ['Code Prompt', 'Context Prompt', 'Comment Prompt', 'Pane Prompt']

acc = np.array([a_prompt[0]/ sum(a_prompt) * 100, a_prompt[3]/ sum(a_prompt) * 100, a_prompt[1]/ sum(a_prompt) * 100, a_prompt[2]/ sum(a_prompt) * 100])
exp = np.array([e_prompt[0]/ sum(e_prompt) * 100, e_prompt[3]/ sum(e_prompt) * 100, e_prompt[1]/ sum(e_prompt) * 100, e_prompt[2]/ sum(e_prompt) * 100])

width = 0.35

fig, ax = plt.subplots()

ax.bar(labels, acc, width, label='Acceleration', color="#00FFFF")
ax.bar(labels, exp, width, bottom=acc,
       label='Exploration', color="#FA8072")

ax.set_ylabel('% Time spent in each prompting strategy', fontsize=10)
ax.set_title('Prompting strategies in the two interaction modes', fontsize=10)
ax.legend(loc='upper center')
plt.savefig('modes-prompt.pdf')