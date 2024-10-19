import numpy as np
import matplotlib.pyplot as plt
import colors
import utils

BASE_PATH = "data-asplos/keystone-spike/"

KEYSTONE_BASELINE = "keystone-baseline/"
KEYSTONE_ENCLAVE = "keystone-enclave/"
TYCHE_ENCLAVE = "tyche-enclave/"
TYCHE_BASELINE = "tyche-baseline/"

NORX = "norx.txt"
QSORT = "qsort.txt"
SHA512 = "sha512.txt"
MINIZ = "miniz.txt"
DHRYSTONE = "dhrystone.txt"

def remove_worst(data, lower_is_better: bool):
    if lower_is_better:
        data.remove(max(data))
    else:
        data.remove(min(data))

def get_mean_std(data):
    return (float(np.mean(data)), float(np.std(data)))

def parse_rv8(experiment: str, config: str):
    data = []
    path = BASE_PATH + config + experiment
    with open(path, 'r') as file:
        for line in file:
            if not line.startswith("iruntime"):
                continue

            data.append(float(line.split()[1]))

            # We keep at most 10 samples
            if len(data) >= 10:
                break
    if len(data) < 10:
        print(f"WARNING: less than 10 samples in {path}")

    remove_worst(data, lower_is_better = True)
    return get_mean_std(data)

print(parse_rv8(NORX, TYCHE_ENCLAVE))
print(parse_rv8(NORX, TYCHE_BASELINE))

labels = ["norx", "qsort", "sha512", "miniz", "dhrystone"]
lower_is_better = [True, True, True, True, True]

setups = [KEYSTONE_ENCLAVE, TYCHE_BASELINE, TYCHE_ENCLAVE]
expes = [NORX, QSORT, SHA512, MINIZ, DHRYSTONE]

data = []

for setup in setups:
    setup_data = []
    for expe in expes:
        setup_data.append(parse_rv8(expe, setup))
    data.append(setup_data)


print(data)
# ——————————————————————————————————— Plot ——————————————————————————————————— #

def make_relative(ref, data):
    scaled = []
    for i in range(len(ref)):
        r = ref[i]
        d = data[i]
        if lower_is_better[i]:
            scaled.append(r[0]/d[0])
        else:
            scaled.append(d[0]/r[0])
    return scaled

referece = data[0]
for i in range(len(data)):
    data[i] = make_relative(referece, data[i])

def plot_comparison():
    fig, ax = plt.subplots(figsize=(6.4, 1.8))
    
    # Plot the bars
    width = 0.23
    x = np.arange(len(labels))

    # colors
    ctyche = colors.get_tyche()
    cnative = colors.get_native()

    # ax.bar(x - 3.5 * width, [x[0] for x in native], width, label='Native', edgecolor='black', color=cnative[0])
    # ax.bar(x - 2.5 * width, [x[0] for x in native_vm], width, label='Native VM', edgecolor='black', hatch='..', color=cnative[1])
    ax.bar(x - 1.5 * width, data[0], width, label='Native', edgecolor='black', hatch='', color=cnative[0])
    ax.bar(x - 0.5 * width, data[0], width, label='Keystone enclave', edgecolor='black', hatch='//', color=cnative[2])
    ax.bar(x + 0.5 * width, data[1], width, label='TD0', edgecolor='black', color=ctyche[0])
    # ax.bar(x + 0.5 * width, [x[0] for x in themis_vm], width, label='TD1 VM', edgecolor='black', hatch='..', color=ctyche[1])
    # ax.bar(x + 1.5 * width, [x[0] for x in themis_conf], width, label='TD1 CVM', edgecolor='black', hatch='\\\\', color=ctyche[2])
    ax.bar(x + 1.5 * width, data[2], width, label='TD1 enclave', edgecolor='black', hatch='//', color=ctyche[3])
    # ax.bar(x + 3.5 * width, [x[0] for x in themis_conf_gramine], width, label='TD2 enclave', edgecolor='black', hatch='xx', color=ctyche[4])

    plt.xticks(x, labels)
    ax.axhline(y=1, color='black', linestyle='--')
    ax.set_ylim(0, 1.1)
    ax.set(ylabel='RV8 performance\nrelative to native',
           title='')
    ax.legend(loc='lower right')

    utils.plot_or_save("rv8")

plot_comparison()
