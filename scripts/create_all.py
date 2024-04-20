import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D

X86_PATH = "../data/ubench/create_all_merged.txt"
RISCV_PATH = "../data/ubench/create_all_merged_riscv_2.txt"

save_as_pdf = "../figs/create-revoke.pdf"
save_as_png = "../figs/create-revoke.png"

cmap = mpl.colormaps['Set2']
colors = cmap(np.linspace(0, 1, 9))
color_enclave = colors[0] #"royalblue"
color_carve = colors[1] #"darkorange"
color_alias = colors[2] # "darkorchid"


def process(path: str):
    raw_data = {}

    with open(path, 'r') as file:
      csvreader = csv.reader(file)
      for row in csvreader:
        # print(row)
        exp = row[0][4:]
        if not exp in raw_data:
            raw_data[exp] = {"create": [], "destroy": []}
            # We skip the first run each time, it's the warm-up run
        else:
            raw_data[exp]["create"].append(float(row[1]))
            raw_data[exp]["destroy"].append(float(row[2]))

    print(raw_data)

    data = {}
    for (exp, values) in raw_data.items():
        [kind, size] = exp.split("//")
        unit = size[-1]
        size = int(size[:-1])
        if unit == 'M':
            size = size * 1024
        if not kind in data:
            data[kind] = []
        data[kind].append({
            "size": size,
            "create_mean": np.mean(values["create"]),
            "create_std": np.std(values["create"]),
            "destroy_mean": np.mean(values["destroy"]),
            "destroy_std": np.std(values["destroy"]),
        })

    for exp in data.keys():
        data[exp].sort(key = lambda x: x["size"])
    return data

x86_data = process(X86_PATH)
rv_data = process(RISCV_PATH)

def get_sizes(exp):
    return [x["size"] for x in exp]

def get_val_err_create(exp):
    return ([x["create_mean"] for x in exp], [x["create_std"] for x in exp])

def get_val_err_destroy(exp):
    return ([x["destroy_mean"] for x in exp], [x["destroy_std"] for x in exp])


# fig, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
fig, (ax0, ax1) = plt.subplots(ncols=2, sharey=True, figsize=(6.0, 2.2))

# x86_64

sizes = get_sizes(x86_data["enclaves"])
(enc, enc_err) = get_val_err_create(x86_data["enclaves"])
(car, car_err) = get_val_err_create(x86_data["carve"])
(san, san_err) = get_val_err_create(x86_data["sandboxes"])
(encd, encd_err) = get_val_err_destroy(x86_data["enclaves"])
(card, card_err) = get_val_err_destroy(x86_data["carve"])
(sand, sand_err) = get_val_err_destroy(x86_data["sandboxes"])

ax0.errorbar(sizes, enc, marker="1", label="Enclaves", color=color_enclave)
ax0.errorbar(sizes, car, marker="2", label="Carved", color=color_carve)
ax0.errorbar(sizes, san, marker="3", label="Sandboxes", color=color_alias)
ax0.errorbar(sizes, encd, fmt='--', marker="1", label="Enclaves", color=color_enclave)
ax0.errorbar(sizes, card, fmt='--', marker="2", label="Carved", color=color_carve)
ax0.errorbar(sizes, sand, fmt='--', marker="3", label="Sandboxes", color=color_alias)
ax0.set_xscale('log', base=2)
ax0.set_yscale('log', base=10)
ax0.set_ylabel('Elapsed time (µs)')
# ax0.legend()
ax0.set_title("x86_64")

# RISC-V

(enc, enc_err) = get_val_err_create(rv_data["enclaves"])
(car, car_err) = get_val_err_create(rv_data["carve"])
(san, san_err) = get_val_err_create(rv_data["sandboxes"])
(encd, encd_err) = get_val_err_destroy(rv_data["enclaves"])
(card, card_err) = get_val_err_destroy(rv_data["carve"])
(sand, sand_err) = get_val_err_destroy(rv_data["sandboxes"])

ax1.errorbar(sizes, enc, marker="1", label="Enclaves", color=color_enclave)
ax1.errorbar(sizes, car, marker="2", label="Carved", color=color_carve)
ax1.errorbar(sizes, san, marker="3", label="Sandboxes", color=color_alias)
ax1.errorbar(sizes, encd, fmt='--', marker="1", label="Enclaves", color=color_enclave)
ax1.errorbar(sizes, card, fmt='--', marker="2", label="Carved", color=color_carve)
ax1.errorbar(sizes, sand, fmt='--', marker="3", label="Sandboxes", color=color_alias)
ax1.set_xscale('log', base=2)
ax1.set_yscale('log', base=10)
# ax1.set_ylabel('Elapsed time (µs)')
ax1.set_title("RISC-V")

# Set legend
lines = [
    Line2D([0], [0], label='manual line', marker="1", color=color_enclave),
    Line2D([0], [0], label='manual line', marker="1", color=color_enclave, linestyle='--'),
    Line2D([0], [0], label='manual line', marker="2", color=color_carve),
    Line2D([0], [0], label='manual line', marker="2", color=color_carve, linestyle='--'),
    Line2D([0], [0], label='manual line', marker="3", color=color_alias),
    Line2D([0], [0], label='manual line', marker="3", color=color_alias, linestyle='--'),
]
labels = [
    "Enclave creation",
    "Enclave revocation",
    "Carved creation",
    "Carved revocation",
    "Sandbox creation",
    "Sandbox revocation"
]
# ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=False, ncol=3)
plt.legend(lines, labels, loc='lower center', bbox_to_anchor=(-0.15, -0.47), fancybox=False, ncol=3, labelspacing=-0.06, columnspacing=0.8, frameon=False)
fig.subplots_adjust(bottom=0.25)
plt.rc("legend", fontsize=20)

pow_min = 3
pow_max = 10
ax0.set_xlim([2**pow_min, 2**pow_max])
ax1.set_xlim([2**pow_min, 2**pow_max])

labels = []
for i in range(pow_min-2, pow_max+1, 2):
    print(i)
    val = 2**i 
    if val >= 1024:
        labels.append(f"{val // 1024}MB")
    else:
        labels.append(f"{val}KB")
# print(ax1.get_xticklabels())
# print(labels)
ax0.set_xticklabels(labels)
ax1.set_xticklabels(labels)
# plt.tight_layout()
# plt.show()
plt.savefig(save_as_pdf, bbox_inches='tight')
plt.savefig(save_as_png, bbox_inches='tight')
