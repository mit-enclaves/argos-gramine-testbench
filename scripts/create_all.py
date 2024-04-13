import csv
import numpy as np
import matplotlib.pyplot as plt

PATH = "../data/ubench/create_all_merged.txt"

raw_data = {}

with open(PATH, 'r') as file:
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
print(data)


def get_sizes(exp):
    return [x["size"] for x in exp]

def get_val_err_create(exp):
    return ([x["create_mean"] for x in exp], [x["create_std"] for x in exp])

def get_val_err_destroy(exp):
    return ([x["destroy_mean"] for x in exp], [x["destroy_std"] for x in exp])


fig, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)

sizes = get_sizes(data["enclaves"])
(enc, enc_err) = get_val_err_create(data["enclaves"])
(car, car_err) = get_val_err_create(data["carve"])
(san, san_err) = get_val_err_create(data["sandboxes"])

ax0.errorbar(sizes, enc, yerr=enc_err, label="Enclaves")
ax0.errorbar(sizes, car, yerr=car_err, label="Carved")
ax0.errorbar(sizes, san, yerr=san_err, label="Sandboxes")
ax0.set_xscale('log', base=2)
ax0.set_yscale('log', base=10)
ax0.legend()
ax0.set_title("Creation time")

(enc, enc_err) = get_val_err_destroy(data["enclaves"])
(car, car_err) = get_val_err_destroy(data["carve"])
(san, san_err) = get_val_err_destroy(data["sandboxes"])

ax1.errorbar(sizes, enc, yerr=enc_err, label="Enclaves")
ax1.errorbar(sizes, car, yerr=car_err, label="Carved")
ax1.errorbar(sizes, san, yerr=san_err, label="Sandboxes")
ax1.set_xscale('log', base=2)
ax1.set_yscale('log', base=10)
ax1.set_title("Destruction time")

pow_min = 3
pow_max = 10
ax0.set_xlim([2**pow_min, 2**pow_max])
ax1.set_xlim([2**pow_min, 2**pow_max])

labels = []
for i in range(pow_min-1, pow_max+1):
    print(i)
    val = 2**i 
    if val >= 1024:
        labels.append(f"{val // 1024}M")
    else:
        labels.append(f"{val}K")
# print(ax1.get_xticklabels())
# print(labels)
ax1.set_xticklabels(labels)

plt.show()

