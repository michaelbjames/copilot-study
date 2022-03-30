import os

VERTICAL_COMMAND = {"up": -1, "down": 1}

def get_instructions(l):
    return [tuple(_l.split()) for _l in l]

def solution1(l):
    x = 0
    y = 0
    instuctions = get_instructions(l)
    for command, value in instuctions:
        if command == "forward":
            x += int(value)
        else:
            y += VERTICAL_COMMAND[command] * int(value)
    return x * y


def solution2(l):
    x = 0
    aim = 0
    depth = 0
    instuctions = get_instructions(l)
    for command, value in instuctions:
        if command == "forward":
            x += int(value)
            depth += int(value) * aim
        else:
            aim += VERTICAL_COMMAND[command] * int(value)
    return x * depth


if __name__ == "__main__":
    dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(dir, "input-day2.txt")) as file:
        data = file.read().splitlines()

    print(solution1(data))
    print(solution2(data))