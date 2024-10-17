import json
import numpy as np
import matplotlib.pyplot as plt
import colors
import utils

SGX_PATH = "data-asplos/gramine-sgx/"
GRAMINE_TYCHE_PATH = "data-asplos/gramine-tyche/"
THEMIS_VM_PATH = "data-asplos/themis-vm/"
THEMIS_CONF_PATH = "data-asplos/themis-conf/"
THEMIS_CONF_GRAMINE_PATH = "data-asplos/themis-conf-gramine/"
TYCHE_PATH = "data-asplos/tyche/"
NATIVE_PATH = "data-asplos/native/"
NATIVE_VM_PATH = "data-asplos/native-vm/"

HYPER = "hyper.txt"
REDIS = "redis.json"
LIGHTTPD = "lighttpd-10K.txt"
LLAMA = "llama.txt"

REQUESTS_SECS = "Requests/sec:"
BYTES_SECS = "Transfer/sec:"

# Change the font
plt.rcParams.update({'font.size': 12})

def as_bytes(data: str):
    if data.endswith("MB"):
        return data[:-2]
    else:
        print(f"ERROR: format not yet handled '{data}'")

def remove_worst(data, lower_is_better: bool):
    if lower_is_better:
        data.remove(max(data))
    else:
        data.remove(min(data))

def get_mean_std(data):
    return (float(np.mean(data)), float(np.std(data)))

def parse_wrk(path: str, label: str):
    data = []
    with open(path, 'r') as file:
        for line in file:
            if not line.startswith(label):
                continue

            raw_data = line.split()[1]
            if label == BYTES_SECS:
                raw_data = as_bytes(raw_data)

            req_per_sec = float(raw_data)
            data.append(req_per_sec)

            # We keep at most 10 samples
            if len(data) >= 10:
                break
    if len(data) < 10:
        print(f"WARNING: less than 10 samples in {path}")
    remove_worst(data, lower_is_better = False)
    return get_mean_std(data)

def parse_speedsqlite(path: str):
    data = []
    with open(path + "sqlite.txt", 'r') as file:
        for line in file:
            if not line.strip().startswith("TOTAL"):
                continue

            raw_data = line.split()[1][:-1]
            data.append(float(raw_data))

            # We keep at most 10 samples
            if len(data) >= 10:
                break
    if len(data) < 10:
        print(f"WARNING: less than 10 samples in {path}")
    remove_worst(data, lower_is_better = True)
    return get_mean_std(data)

def parse_redis(path: str):
    data = None
    with open(path + "redis.json", 'r') as file:
        data = json.load(file)
    # For now we don't have variance for Redis bench
    return [data["ALL STATS"]["Totals"]["Ops/sec"], 0]

def parse_llama(path: str):
    data = []
    with open(path + "llama.txt", 'r') as file:
        for line in file:
            if "99 runs" in line:
               time = float(line.split()[-4])
               data.append(time)

            # We keep at most 10 samples
            if len(data) >= 10:
                break

    if len(data) < 10:
        print(f"WARNING: less than 10 samples in {path}")
    remove_worst(data, lower_is_better = False)
    return get_mean_std(data)


labels = ["redis", "hyper", "lighttpd", "sqlite", "llama"]
units = ["req/s","req/s", "MiB/s", "s", "token/s"]
display = [
    lambda x: f"{round(x/1000)}k",
    lambda x: f"{round(x/1000)}k",
    lambda x: f"{x:.1f}",
    lambda x: f"{x:.2f}",
    lambda x: f"{x:.2f}",
]
lower_is_better = [False, False, False, True, False]

native = []
native_vm = []
gramine_sgx = []
themis_vm = []
themis_conf = []
themis_conf_gramine = []
gramine_tyche = []
tyche = []

# —————————————————————————————————— Redis ——————————————————————————————————— #

native.append(parse_redis(NATIVE_PATH))
native_vm.append(parse_redis(NATIVE_VM_PATH))
gramine_sgx.append(parse_redis(SGX_PATH))
themis_vm.append(parse_redis(THEMIS_VM_PATH))
themis_conf.append(parse_redis(THEMIS_CONF_PATH))
themis_conf_gramine.append(parse_redis(THEMIS_CONF_GRAMINE_PATH))
gramine_tyche.append(parse_redis(GRAMINE_TYCHE_PATH))
tyche.append(parse_redis(TYCHE_PATH))

# —————————————————————————————————— Hyper ——————————————————————————————————— #

native.append(parse_wrk(NATIVE_PATH + HYPER, REQUESTS_SECS))
native_vm.append(parse_wrk(NATIVE_VM_PATH + HYPER, REQUESTS_SECS))
gramine_sgx.append(parse_wrk(SGX_PATH + HYPER, REQUESTS_SECS))
themis_vm.append(parse_wrk(THEMIS_VM_PATH + HYPER, REQUESTS_SECS))
themis_conf.append(parse_wrk(THEMIS_CONF_PATH + HYPER, REQUESTS_SECS))
themis_conf_gramine.append(parse_wrk(THEMIS_CONF_GRAMINE_PATH + HYPER, REQUESTS_SECS))
gramine_tyche.append(parse_wrk(GRAMINE_TYCHE_PATH + HYPER, REQUESTS_SECS))
tyche.append(parse_wrk(TYCHE_PATH + HYPER, REQUESTS_SECS))

print(f"SGX:           {gramine_sgx[0][0]:.2f} +/- {gramine_sgx[0][0]:.2f} Req/Sec")
print(f"Gramine Tyche: {gramine_tyche[0][0]:.2f} +/- {gramine_tyche[0][0]:.2f} Req/Sec")
print(f"THEMIS CVM:    {themis_conf[0][0]:.2f} +/- {themis_conf[0][0]:.2f} Req/Sec")
print(f"  Tyche is {gramine_tyche[0][0] / gramine_sgx[0][0]:.2f}x faster than SGX")

# ————————————————————————————————— Lighttpd ————————————————————————————————— #

native.append(parse_wrk(NATIVE_PATH + LIGHTTPD, BYTES_SECS))
native_vm.append(parse_wrk(NATIVE_VM_PATH + LIGHTTPD, BYTES_SECS))
gramine_sgx.append(parse_wrk(SGX_PATH + LIGHTTPD, BYTES_SECS))
themis_vm.append(parse_wrk(THEMIS_VM_PATH + LIGHTTPD, BYTES_SECS))
themis_conf.append(parse_wrk(THEMIS_CONF_PATH + LIGHTTPD, BYTES_SECS))
themis_conf_gramine.append(parse_wrk(THEMIS_CONF_GRAMINE_PATH + LIGHTTPD, BYTES_SECS))
gramine_tyche.append(parse_wrk(GRAMINE_TYCHE_PATH + LIGHTTPD, BYTES_SECS))
tyche.append(parse_wrk(TYCHE_PATH + LIGHTTPD, BYTES_SECS))

# —————————————————————————————————— Sqlite —————————————————————————————————— #

native.append(parse_speedsqlite(NATIVE_PATH))
native_vm.append(parse_speedsqlite(NATIVE_VM_PATH))
gramine_sgx.append(parse_speedsqlite(SGX_PATH))
themis_vm.append(parse_speedsqlite(THEMIS_VM_PATH))
themis_conf.append(parse_speedsqlite(THEMIS_CONF_PATH))
themis_conf_gramine.append(parse_speedsqlite(THEMIS_CONF_GRAMINE_PATH))
gramine_tyche.append(parse_speedsqlite(GRAMINE_TYCHE_PATH))
tyche.append(parse_speedsqlite(TYCHE_PATH))

# —————————————————————————————————— Llama ——————————————————————————————————— #

native.append(parse_llama(NATIVE_PATH))
native_vm.append(parse_llama(NATIVE_VM_PATH))
gramine_sgx.append(parse_llama(SGX_PATH))
themis_vm.append(parse_llama(THEMIS_VM_PATH))
themis_conf.append(parse_llama(THEMIS_CONF_PATH))
themis_conf_gramine.append(parse_llama(THEMIS_CONF_GRAMINE_PATH))
gramine_tyche.append(parse_llama(GRAMINE_TYCHE_PATH))
tyche.append(parse_llama(TYCHE_PATH))

# ——————————————————————————————————— Plot ——————————————————————————————————— #

def make_relative(ref, data):
    scaled = []
    for i in range(len(ref)):
        r = ref[i]
        d = data[i]
        if lower_is_better[i]:
            scaled.append((r[0]/d[0], r[0]/d[1]))
        else:
            scaled.append((d[0]/r[0], d[1]/r[0]))
    return scaled

referece = native

themis_conf_gramine = make_relative(native, themis_conf_gramine)
themis_conf = make_relative(native, themis_conf)
themis_vm = make_relative(native, themis_vm)
gramine_tyche = make_relative(native, gramine_tyche)
gramine_sgx = make_relative(native, gramine_sgx)
tyche = make_relative(native, tyche)
native_vm = make_relative(native, native_vm)
native = make_relative(native, native)

# print(themis_conf)
# print(gramine_tyche)
# print(gramine_sgx)
# print(native)

def plot_comparison():
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    
    # Plot the bars
    width = 0.11
    x = np.arange(len(labels))

    # colors
    ctyche = colors.get_tyche()
    cnative = colors.get_native()

    ax.bar(x - 3.5 * width, [x[0] for x in native], width, label='Native', edgecolor='black', color=cnative[0])
    ax.bar(x + 0.5 * width, [x[0] for x in themis_vm], width, label='TD1 VM', edgecolor='black', hatch='..', color=ctyche[1])
    ax.bar(x - 2.5 * width, [x[0] for x in native_vm], width, label='Native VM', edgecolor='black', hatch='..', color=cnative[1])
    ax.bar(x + 1.5 * width, [x[0] for x in themis_conf], width, label='TD1 CVM', edgecolor='black', hatch='\\\\', color=ctyche[2])
    ax.bar(x - 1.5 * width, [x[0] for x in gramine_sgx], width, label='SGX enclave', edgecolor='black', hatch='//', color=cnative[2])
    ax.bar(x + 2.5 * width, [x[0] for x in gramine_tyche], width, label='TD1 enclave', edgecolor='black', hatch='//', color=ctyche[3])
    ax.bar(x - 0.5 * width, [x[0] for x in tyche], width, label='TD0', edgecolor='black', color=ctyche[0])
    ax.bar(x + 3.5 * width, [x[0] for x in themis_conf_gramine], width, label='TD2 enclave', edgecolor='black', hatch='xx', color=ctyche[4])

    plt.xticks(x, labels)
    ax.axhline(y=1, color='black', linestyle='--')
    ax.set_ylim(0, 1.1)
    ax.set(ylabel='Performance relative to Native')
    ax.legend(loc='lower center',  bbox_to_anchor=(0.5, -0.4), ncol=4)

    
    for i in range(len(referece)):
        score = referece[i][0]
        unit = units[i]
        ax.annotate(f'{display[i](score)}{unit}',
                    xy=(x[i], 1.02),
                    ha='center', va='bottom')
    
    utils.plot_or_save("perf_comparison")

plot_comparison()
