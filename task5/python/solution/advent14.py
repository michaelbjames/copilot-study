from collections import Counter, defaultdict

def part_one(filename: str) -> int:
    template, rules = parse_input(filename)
    # here you actually construct the new template then counted the number of pairs
    for _ in range(10):
        new_template = ""
        for i in range(len(template) - 1):
            pair = template[i : i + 2]
            new_template += pair[0]
            if pair in rules:
                new_template += rules[pair]
        new_template += pair[1]
        template = new_template

    counters = Counter(template)
    return max(counters.values()) - min(counters.values())


def part_two(filename: str) -> int:
    template, rules = parse_input(filename)
    count_pairs = defaultdict(int)
    for i in range(len(template) - 1):
        count_pairs[template[i : i + 2]] += 1

    ## count the pairs without constructing the new template
    for _ in range(40):
        new_count_pairs = defaultdict(int)
        for pair, count in count_pairs.items():
            new_count_pairs[pair[0] + rules[pair]] += count
            new_count_pairs[rules[pair] + pair[1]] += count
        count_pairs = new_count_pairs

    counters = defaultdict(int)
    for pair in count_pairs:
        for ch in pair:
            counters[ch] += count_pairs[pair]
    
    # if even divide by 2, if odd (chars on edges) add 1 and divide by 2
    counters = {k: (v + 1) // 2 for k, v in counters.items()}
    return max(counters.values()) - min(counters.values())

def parse_input(filename):
    with open(filename) as f:
        template, rules = f.read().split("\n\n")
    rules = list(
        map(lambda rule: rule.strip().split(" -> "), rules.strip().split("\n"))
    )
    rules = {rule[0]: rule[1] for rule in rules}
    return template, rules

if __name__ == "__main__":
    input_path = "input-day14.txt"
    print("---Part One---")
    print(part_one(input_path))

    print("---Part Two---")
    print(part_two(input_path))