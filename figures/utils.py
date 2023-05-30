import pandas as pd

def sort_by_first(tuples):
    return sorted(tuples, key=lambda x: x[0])

def process_input(pid):
    df = pd.DataFrame(pd.read_excel(f"exports/p{pid}-export.xlsx".format(pid=pid)))
    start_codes = list(map(lambda x: float(x[2:].split(',')[0].replace(':', '.')), df['Beginning'].tolist()))
    end_codes = list(map(lambda x: float(x[2:].split(',')[0].replace(':', '.')), df['End'].tolist()))
    labels = df['Code'].tolist()
    codes_tuple = list(zip(start_codes, end_codes, labels))
    return sort_by_first(codes_tuple)

def time_spent(code, codes):
    total_time = 0
    for c in codes:
        if c[2] == code:
            total_time += (c[1] - c[0])
    return total_time

def time_spent_validate(code, codes):
    total_time = 0
    for c in codes:
        if code in c[2]:
           total_time += (c[1] - c[0])
    return total_time

def get_total_time(codes):
    total_time = codes[-1][1] - codes[0][0]
    return total_time

def time_spent_special(code, codes, start, end):
    total_time = 0
    for c in codes:
        if c[0] >= start and c[1] <= end:
            if c[2] == code:
                total_time += (c[1] - c[0])
    return total_time

def times_split(num):
    rust_start, rust_end, py_start, py_end, acc_times_rust, exp_times_rust, acc_times_py, exp_times_py = [], [], [], [], [], [], [], []
    codes = process_input(num)
    for code in codes:
        if "rust-starts" in code[2]:
            rust_start.append(code[1])
        elif "rust-ends" in code[2]:
            rust_end.append(code[1])
        elif "python-starts" in code[2]:
            py_start.append(code[1])
        elif "python-ends" in code[2]:
            py_end.append(code[1])
    acc_times_rust.append(time_spent_special("acceleration", codes, rust_start[0], rust_end[0]))
    acc_times_rust.append(time_spent_special("acceleration", codes, rust_start[1], rust_end[1]))
    exp_times_rust.append(time_spent_special("exploration", codes, rust_start[0], rust_end[0]))
    exp_times_rust.append(time_spent_special("exploration", codes, rust_start[1], rust_end[1]))
    acc_times_py.append(time_spent_special("acceleration", codes, py_start[0], py_end[0]))
    acc_times_py.append(time_spent_special("acceleration", codes, py_start[1], py_end[1]))
    exp_times_py.append(time_spent_special("exploration", codes, py_start[0], py_end[0]))
    exp_times_py.append(time_spent_special("exploration", codes, py_start[1], py_end[1]))
    return (sum(acc_times_rust), sum(exp_times_rust), sum(acc_times_py), sum(exp_times_py))
