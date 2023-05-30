from operator import contains
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import matplotlib.patches as mpatches


bg_color = "#FFFFFF"

light_color =  "#00B6F2"
medium_color = "#007CA6"

# Lighter to darker (state, prompting, validation)
exp_color = "#F79C9C"
exp_prompt = "#DC143C"
exp_validate = "#8B0000"

exp_patch = mpatches.Patch(color=exp_color, label='Exploration')
exp_prompt_patch = mpatches.Patch(color=exp_prompt, label='Exploration Prompt')
exp_validate_patch = mpatches.Patch(color=exp_validate, label='Exploration Validation')

acc_color = "#83CAF7"
acc_prompt = "#2396DE"
acc_validate = "#0F405E"

acc_patch = mpatches.Patch(color=acc_color, label='Acceleration')
acc_prompt_patch = mpatches.Patch(color=acc_prompt, label='Acceleration Prompt')
acc_validate_patch = mpatches.Patch(color=acc_validate, label='Acceleration Validation')

REJECT_COLOR = "#D427E0"
ACCEPT_COLOR = "#0A9428"
REPAIR_COLOR = "#949028"
repair_patch = mpatches.Patch(color=REPAIR_COLOR, label='Repair')
reject_patch = mpatches.Patch(color=REJECT_COLOR, label='Reject')
accept_patch = mpatches.Patch(color=ACCEPT_COLOR, label='Accept')


ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

def sort_by_first(tuples):
    return sorted(tuples, key=lambda x: x[0])

def process_input(pid):
    df = pd.DataFrame(pd.read_excel(f"exports/p{pid}-export.xlsx".format(pid=pid)))
    start_codes = list(map(lambda x: float(x[2:].split(',')[0].replace(':', '.')), df['Beginning'].tolist()))
    end_codes = list(map(lambda x: float(x[2:].split(',')[0].replace(':', '.')), df['End'].tolist()))
    labels = df['Code'].tolist()
    codes_tuple = list(zip(start_codes, end_codes, labels))
    return sort_by_first(codes_tuple)

def get_longest_time():
    longest_time = 0
    for pid in ids:
        codes = process_input(pid)
        total_time = codes[-1][1] - codes[0][0]
        if total_time > longest_time:
            longest_time = total_time
    return longest_time

longest_time = get_longest_time()

def timeline_ycenter(pid):
    yr = timeline_yrange(pid)
    return yr[0] + 0.5 * yr[1]

def timeline_yrange(pid):
    width = 0.5
    return (ids.index(pid) + 1 - (width / 2), width)

chunk_styles = {
    "acc/prompt/multi-menu": (acc_prompt, "xx"),
    "acc/prompt/context": (acc_prompt, "xx"),
    "acc/prompt/code": (acc_prompt, "xx"),
    "acc/prompt/nl": (acc_prompt, "xx"),

    "acc/modify/inline": (medium_color, "----"),
    "acc/modify/multi-line": (medium_color, "----"),
    "acc/accept/inline": (medium_color, "----"),
    "acc/reject/inline": (medium_color, "----"),
    "acc/accept/prompt": (medium_color, "----"),
    "acc/reject/multi-line":(medium_color, "----"),
    "acc/accept/multi-line":(medium_color, "----"),

    "acc/validate/examine/multi-menu": (acc_validate, ".."),
    "acc/validate/run(plot)": (acc_validate, ".."),
    "acc/validate/run": (acc_validate, ".."),
    "acc/validate/examine/inline": (acc_validate, ".."),
    "acc/validate/examine": (acc_validate, ".."),
    "acc/validate/api(in-ide)" : (acc_validate, ".."),
    "acc/validate/compile": (acc_validate, ".."),
    "validate/acc/run": (acc_validate, ".."),
    "acc/validate/IDE": (acc_validate, ".."),
    "acc/validate/examine/multi-snip": (acc_validate, ".."),
    "acc/validate/examine/multi-line": (acc_validate, ".."),

    "start-code": (acc_validate, "xx"),

    "exp/prompt/multiple-menu": (exp_prompt, "xx"),
    "exp/prompt/multi-menu": (exp_prompt, "xx"),
    "exp/prompt/multi-menu/nudge": (exp_prompt, "xx"),
    "exp/prompt/code": (exp_prompt, "xx"),
    "exp/prompt/nl": (exp_prompt, "xx"),
    "exp/prompt/context": (exp_prompt, "xx"),
    "exp/prompt/nl/nudge": (exp_prompt, "xx"),

    "exp/modify/inline": (exp_color, "----"),
    "exp/accept/inline": (exp_color, "----"),
    "exp/reject/multi-menu": (exp_color, "----"),
    "exp/modify/multi-menu": (exp_color, "----"),
    "exp/accept/multi-menu": (exp_color, "----"),
    "exp/reject/inline": (exp_color, "----"),
    "exp/accept/prompt": (exp_color, "----"),
    "exp/reject/code": (exp_color, "----"),
    "reject/multi-menu": (exp_color, "----"),
    "exp/accept/multi-menu/sub-snippet": (exp_color, "----"),
    "exp/modify/multi-menu/sub-snippet": (exp_color, "----"),
    "exp/reject/multi-line": (exp_color, "----"),
    "exp/accept/multi-menu/subsnippet": (exp_color, "----"),
    "exp/accept/multi-menu/nudge": (exp_color, "----"),

    "exp/validate/examine/multi-menu": (exp_validate, ".."),
    "exp/validate/examine/multi-menu'": (exp_validate, ".."),
    "expl/validate/google": (exp_validate, ".."),
    "expl/validate/inline": (exp_validate, ".."),
    "exp/validate/inline": (exp_validate, ".."),
    "exp/validate/run(plot)": (exp_validate, ".."),
    "exp/validate/run": (exp_validate, ".."),
    "exp/validate/examine/multi-menu": (exp_validate, ".."),
    "exp/validate/examine/inline": (exp_validate, ".."),
    "exp/validate/api(in-ide)": (exp_validate, ".."),
    "exp/validate/examine/api(in-ide)": (exp_validate, ".."),
    "exp/validate/google": (exp_validate, ".."),
    "exp/examine/validate/inline": (exp_validate, ".."),
    "exp/validate/examine": (exp_validate, ".."),
    "exp/validate/api(google)" : (exp_validate, ".."),
    "exp/validate/api-docs(google)" : (exp_validate, ".."),
    "exp/validate/in-ide(errors)" : (exp_validate, ".."),
    "exp/validate/compile" : (exp_validate, ".."),
    "exp/validate/debugger" : (exp_validate, ".."),
    "exp/validate/api/ide" : (exp_validate, ".."),
    "exp/validate/examine/multi-line": (exp_validate, ".."),
    "exp/validate/api/web": (exp_validate, ".."),
    "exp/validate/api/web/multi-snip": (exp_validate, ".."),
    "exp/validate/examine/exp/validate/examine/spec": (exp_validate, ".."),
    "exp/validate/api": (exp_validate, ".."),

    "end-code": (bg_color, ""),

    "exploration": (exp_color, ""),
    "acceleration": (acc_color, ""),

    "rust-starts": (bg_color, ""),
    "rust-ends": (bg_color, ""),
    "python-starts": (bg_color, ""),
    "python-ends": (bg_color, ""),
}

chunk_edgecolor = "black"

def get_total_time(codes):
    total_time = codes[-1][1] - codes[0][0]
    return total_time

def scaling_factor(codes):
    return longest_time / get_total_time(codes)

def normalize_code(user_codes):
    offset = user_codes[0][0]
    sf = scaling_factor(user_codes)
    new_codes = []
    for code in user_codes[1:-1]:  # skip first and last
        new_codes.append(((code[0] - offset) * sf, (code[1] - offset) * sf, code[2]))
    return new_codes

def plot_action_chunk(pid, ax, start_time, end_time, chunk, codes):
    code_start_time = start_time * scaling_factor(codes)
    code_duration = (end_time - start_time) * scaling_factor(codes)
    ACTION_Y_EXTRA = 0.2
    y_min = timeline_yrange(pid)[0] - ACTION_Y_EXTRA
    action_kwargs = {
        "x": code_start_time,
        "ymin": y_min,
        "ymax": timeline_yrange(pid)[0]+timeline_yrange(pid)[1]+ACTION_Y_EXTRA,
        "linewidth": 1,
    }
    ax.set_axisbelow(False)
    if "reject" in chunk:
        ax.vlines(colors=REJECT_COLOR, **action_kwargs)
    elif "accept" in chunk:
        ax.vlines(colors=ACCEPT_COLOR, **action_kwargs)
    elif "modify" in chunk:
        ax.vlines(colors=REPAIR_COLOR, **action_kwargs)
    # The rest
    elif "reject" not in chunk and "accept" not in chunk and "modify" not in chunk and "start-code" not in chunk and "end-code" not in chunk and "acceleration" not in chunk and "exploration" not in chunk:
        ax.broken_barh(
        [(code_start_time, code_duration)],
        timeline_yrange(pid),
        facecolor = chunk_styles[chunk][0],
        edgecolor = chunk_edgecolor,
        linewidth = 0.1,
        zorder=2.5,
    )

def plot_mode_chunk(pid, ax, start_time, end_time, chunk, codes):
    ax.set_axisbelow(True)
    code_start_time = start_time  * scaling_factor(codes)
    code_end_time = end_time * scaling_factor(codes)
    if "acceleration" in chunk:
        y_mid = (timeline_yrange(pid)[0] + (timeline_yrange(pid)[0]+timeline_yrange(pid)[1])) / 2
        ax.hlines(y_mid, code_start_time, code_end_time, color=acc_color)
    elif "exploration" in chunk:
        y_mid = (timeline_yrange(pid)[0] + (timeline_yrange(pid)[0]+timeline_yrange(pid)[1])) / 2
        ax.hlines(y_mid, code_start_time, code_end_time, color=exp_color)

fig, ax = plt.subplots()

for i in ids:
    codes = process_input(i)
    # codes = normalize_code(codes)
    offset = codes[0][0]
    for code in codes:
        plot_mode_chunk(i, ax, code[0] - offset, code[1] - offset, code[2], codes)
    for code in codes:
        plot_action_chunk(i, ax, code[0] - offset, code[1] - offset, code[2], codes)

ax.set_xlabel("Percent of study completed")
ax.set_xticks([])


ax.set_ylabel("Participant number")
ax.set_yticks(range(1, len(ids) + 1))
ax.set_yticklabels(ids)

lgd = ax.legend(
    handles=[
        acc_patch,
        acc_prompt_patch,
        acc_validate_patch,
        exp_patch,
        exp_prompt_patch,
        exp_validate_patch,
        accept_patch,
        repair_patch,
        reject_patch,
    ],
    labels = [
        "Acceleration",
        "Acceleration - Prompting",
        "Acceleration - Validating",
        "Exploration",
        "Exploration - Prompting",
        "Exploration - Validating",
        "Accept Suggestion",
        "Repair Suggestion",
        "Reject Suggestion",
    ],
    loc="lower left",
    bbox_to_anchor=(0.05,-0.25),
    ncol=3,
    prop={'size': 8},
)

# set figure size
fig.set_size_inches(8, 4.5)

#plt.show()
plt.savefig("chunks.pdf",
    dpi=600,
    bbox_extra_artists=(lgd,), bbox_inches='tight')