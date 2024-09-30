import os
import numpy as np
import matplotlib.pyplot as plt

exp = [
    ("Linux Native", "../data/ubench/coremark_linux.txt"),
    ("Anon Native", "../data/ubench/coremark_tyche.txt"),
    ("Linux VM", "../data/ubench/coremark_linux_vm_1.txt"),
    ("Anon VM", "../data/ubench/coremark_tyche_vm_1.txt"),
]

NATIVE_PATH = "data-asplos/coremark-native/"
NATIVE = "native"
THEMIS_PATH = "data-asplos/coremark-themis/"
THEMIS = "sdktyche"

raw_data = {}

def parse_data(exp: str, path: str):
    for filename in os.listdir(path):
        prefix = filename.split(".")[0]
        nb_cores = int(prefix.split("_")[1])
        with open(path + filename, "r") as file:
            for line in file.readlines():
                if "CoreMark-PRO" not in line:
                    continue
                score = float(line.split()[1])
                if exp not in raw_data:
                    raw_data[exp] = []
                raw_data[exp].append((nb_cores, score))
                break
    raw_data[exp].sort(key = lambda x: x[0])

parse_data(NATIVE, NATIVE_PATH)
parse_data(THEMIS, THEMIS_PATH)

print(raw_data)

def compute_relative(referece, exp):
    ref_scores = []
    exp_scores = []
    labels = []
    for (nb_cores, score) in exp:
        # Find the reference score for the same number of cores
        ref = None
        for (n, s) in referece:
            if n == nb_cores:
                ref = s
                break

        # If no reference value, skip it
        if ref == None:
            continue

        relative_score = score / ref
        ref_scores.append((1., ref))
        exp_scores.append((relative_score, score))
        labels.append(nb_cores)
        print(f"Scores {relative_score:.3f} for {nb_cores} cores")
    return ref_scores, exp_scores, labels

def plot_curve():
    fig, ax = plt.subplots()
    
    x = [elt[0] for elt in raw_data[NATIVE]]
    y = [elt[1] for elt in raw_data[NATIVE]]
    ax.plot(x, y, label="native")
    
    x = [elt[0] for elt in raw_data[THEMIS]]
    y = [elt[1] for elt in raw_data[THEMIS]]
    ax.plot(x, y, label="themis")
    
    ax.legend()
    ax.set(xlabel='nb cpu', ylabel='CoreMark-Pro score',
           title='Multicore VM scaling')
    ax.grid()
    
    plt.show()

def plot_bar():
    native, themis, labels = compute_relative(raw_data[NATIVE], raw_data[THEMIS])

    print(native)
    print(themis)
    print(labels)

    fig, ax = plt.subplots()
    
    # Plot the bars
    width = 0.35
    x = np.arange(len(labels))

    bars_native = ax.bar(x - width/2, [x[0] for x in native], width, label='Native')
    bars_themis = ax.bar(x + width/2, [x[0] for x in themis], width, label='Themis')

    plt.xticks(x, labels)
    ax.axhline(y=1, color='black', linestyle='--')
    ax.set_ylim(0, 1.18)
    ax.set(xlabel='nb cpu', ylabel='CoreMark-Pro relative score',
           title='Multicore VM scaling')
    ax.legend(loc='lower right')

    def add_values(bars, scores):
        for i in range(len(scores)):
            bar = bars[i]
            score = scores[i][1]
            ax.annotate(f'{int(score)}',
                        xy=(bar.get_x() + bar.get_width() / 2, 1.02),
                        ha='center', va='bottom', rotation=90)
    add_values(bars_themis, themis)
    add_values(bars_native, native)

    # ax.grid()
    
    plt.show()

# plot_curve()
plot_bar()

