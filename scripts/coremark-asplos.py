import os
import numpy as np
import matplotlib.pyplot as plt
import colors
import utils

exp = [
    ("Linux Native", "../data/ubench/coremark_linux.txt"),
    ("Anon Native", "../data/ubench/coremark_tyche.txt"),
    ("Linux VM", "../data/ubench/coremark_linux_vm_1.txt"),
    ("Anon VM", "../data/ubench/coremark_tyche_vm_1.txt"),
]

NATIVE_PATH = "data-asplos/coremark-native/"
NATIVE = "native"
NATIVE_VM_PATH = "data-asplos/coremark-native-vm/"
NATIVE_VM = "native-vm"
TYCHE_PATH = "data-asplos/coremark-tyche/"
TYCHE = "tyche"
THEMIS_VM_PATH = "data-asplos/coremark-themis-vm/"
THEMIS_VM = "themis-vm"
THEMIS_CONF_VM_PATH = "data-asplos/coremark-themis-conf-vm/"
THEMIS_CONF_VM = "themis-conf-vm"

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
parse_data(NATIVE_VM, NATIVE_VM_PATH)
parse_data(TYCHE, TYCHE_PATH)
parse_data(THEMIS_VM, THEMIS_VM_PATH)
parse_data(THEMIS_CONF_VM, THEMIS_CONF_VM_PATH)

print(raw_data)

def compute_relative(referece, exp, name: str):
    ref_scores = []
    exp_scores = []
    labels = []
    print(f"Scores for {name}:")
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
        print(f"  {relative_score:.3f} for {nb_cores} cores")
    return ref_scores, exp_scores, labels

def plot_curve():
    fig, ax = plt.subplots()
    
    x = [elt[0] for elt in raw_data[NATIVE_VM]]
    y = [elt[1] for elt in raw_data[NATIVE_VM]]
    ax.plot(x, y, label="native")
    
    x = [elt[0] for elt in raw_data[THEMIS_VM]]
    y = [elt[1] for elt in raw_data[THEMIS_VM]]
    ax.plot(x, y, label="themis")
    
    ax.legend()
    ax.set(xlabel='nb cpu', ylabel='CoreMark-Pro score',
           title='Multicore VM scaling')
    ax.grid()
    
    plt.show()

def plot_bar():
    native, native_vm, labels = compute_relative(raw_data[NATIVE], raw_data[NATIVE_VM], NATIVE_VM)
    _, tyche, _ = compute_relative(raw_data[NATIVE], raw_data[TYCHE], TYCHE)
    _, themis_vm, _ = compute_relative(raw_data[NATIVE], raw_data[THEMIS_VM], THEMIS_VM)
    _, themis_conf_vm, _ = compute_relative(raw_data[NATIVE], raw_data[THEMIS_CONF_VM], THEMIS_CONF_VM)

    print(native_vm)
    print(themis_vm)
    print(labels)

    fig, ax = plt.subplots()

    # Plot the bars
    width = 0.18
    x = np.arange(len(labels))

    # colors
    ctyche = colors.get_tyche()
    cnative = colors.get_native()

    bars_native         = ax.bar(x - 2 * width, [x[0] for x in native],         width, label='Native', edgecolor='black', hatch='', color=cnative[0])
    bars_native_vm      = ax.bar(x - 1 * width, [x[0] for x in native_vm],      width, label='Native VM', edgecolor='black', hatch='..', color=cnative[1])
    bars_tyche          = ax.bar(x + 0 * width, [x[0] for x in tyche],          width, label='Anon', edgecolor='black', hatch='', color=ctyche[0])
    bars_themis_vm      = ax.bar(x + 1 * width, [x[0] for x in themis_vm],      width, label='Anon VM', edgecolor='black', hatch='..', color=ctyche[1])
    bars_themis_conf_vm = ax.bar(x + 2 * width, [x[0] for x in themis_conf_vm], width, label='Anon Conf VM', edgecolor='black', hatch='\\\\', color=ctyche[2])

    plt.xticks(x, labels)
    ax.axhline(y=1, color='black', linestyle='--')
    ax.set_ylim(0, 1.09)
    ax.set(xlabel='nb cpu', ylabel='CoreMark-Pro relative score',
           title='Multicore VM scaling')
    ax.legend(loc='lower right')

    def add_values(bars, scores):
        for i in range(len(scores)):
            bar = bars[i]
            score = scores[i][1]
            ax.annotate(f'{int(score)}',
                        xy=(bar.get_x() + bar.get_width() / 2, 1.02),
                        ha='center', va='bottom')
    # add_values(bars_native, native)
    # add_values(bars_native_vm, native_vm)
    add_values(bars_tyche, native)
    # add_values(bars_themis_vm, themis_vm)
    # add_values(bars_themis_conf_vm, themis_conf_vm)
    
    utils.plot_or_save("coremark")

# plot_curve()
plot_bar()

