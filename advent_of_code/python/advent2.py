import os

if __name__ == "__main__":
    dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(dir, "input-day2.txt")) as file:
        data = file.read().splitlines()