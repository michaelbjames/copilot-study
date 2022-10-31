import matplotlib
import matplotlib.pyplot as plt

def read_first_digits_from_file(filename):
    with open(filename) as file:
        data = file.read().splitlines()
    return [int(line[0]) for line in data]

fib_first_digits = read_first_digits_from_file("fib.txt")
inverse_first_digits = read_first_digits_from_file("inverse.txt")

# Plot first_digits as a histogram
# overlayed on top of the histogram of
# inverse_first_digits


