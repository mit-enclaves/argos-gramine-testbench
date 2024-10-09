import os
import numpy as np
import matplotlib.pyplot as plt

SGX_PATH = "data-asplos/gramine-sgx/"
GRAMINE_TYCHE_PATH = "data-asplos/gramine-tyche/"
THEMIS_CONF_PATH = "data-asplos/themis-conf/"
TYCHE_PATH = "data-asplos/tyche/"
NATIVE_PATH = "data-asplos/native/"

HYPER = "hyper.txt"
LIGHTTPD = "lighttpd-1K.txt"

REQUESTS_SECS = "Requests/sec:"
BYTES_SECS = "Transfer/sec:"

def as_bytes(data: str):
    if data.endswith("MB"):
        return data[:-2]
    else:
        print(f"ERROR: format not yet handled '{data}'")

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
    return get_mean_std(data)

labels = ["hyper", "lighttpd", "sqlite"]
lower_is_better = [False, False, True]

native = []
gramine_sgx = []
themis_conf = []
gramine_tyche = []

# —————————————————————————————————— Hyper ——————————————————————————————————— #

native.append(parse_wrk(NATIVE_PATH + HYPER, REQUESTS_SECS))
gramine_sgx.append(parse_wrk(SGX_PATH + HYPER, REQUESTS_SECS))
themis_conf.append(parse_wrk(THEMIS_CONF_PATH + HYPER, REQUESTS_SECS))
gramine_tyche.append(parse_wrk(GRAMINE_TYCHE_PATH + HYPER, REQUESTS_SECS))

print(f"SGX:           {gramine_sgx[0][0]:.2f} +/- {gramine_sgx[0][0]:.2f} Req/Sec")
print(f"Gramine Tyche: {gramine_tyche[0][0]:.2f} +/- {gramine_tyche[0][0]:.2f} Req/Sec")
print(f"THEMIS CVM:    {themis_conf[0][0]:.2f} +/- {themis_conf[0][0]:.2f} Req/Sec")
print(f"  Tyche is {gramine_tyche[0][0] / gramine_sgx[0][0]:.2f}x faster than SGX")

# ————————————————————————————————— Lighttpd ————————————————————————————————— #

native.append(parse_wrk(NATIVE_PATH + LIGHTTPD, BYTES_SECS))
gramine_sgx.append(parse_wrk(SGX_PATH + LIGHTTPD, BYTES_SECS))
themis_conf.append(parse_wrk(THEMIS_CONF_PATH + LIGHTTPD, BYTES_SECS))
gramine_tyche.append(parse_wrk(GRAMINE_TYCHE_PATH + LIGHTTPD, BYTES_SECS))

# —————————————————————————————————— Sqlite —————————————————————————————————— #

native.append(parse_speedsqlite(NATIVE_PATH))
gramine_sgx.append(parse_speedsqlite(SGX_PATH))
themis_conf.append(parse_speedsqlite(THEMIS_CONF_PATH))
gramine_tyche.append(parse_speedsqlite(GRAMINE_TYCHE_PATH))

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


themis_conf = make_relative(native, themis_conf)
gramine_tyche = make_relative(native, gramine_tyche)
gramine_sgx = make_relative(native, gramine_sgx)
native = make_relative(native, native)

print(themis_conf)
print(gramine_tyche)
print(gramine_sgx)
print(native)

def plot_comparison():

    fig, ax = plt.subplots()
    
    # Plot the bars
    width = 0.2
    x = np.arange(len(labels))

    ax.bar(x - 1.5 * width, [x[0] for x in native], width, label='Bare metal Linux')
    ax.bar(x - 0.5 * width, [x[0] for x in gramine_sgx], width, label='Gramine SGX')
    ax.bar(x + 0.5 * width, [x[0] for x in gramine_tyche], width, label='Gramine Anon')
    ax.bar(x + 1.5 * width, [x[0] for x in themis_conf], width, label='Anon CVM')

    plt.xticks(x, labels)
    ax.axhline(y=1, color='black', linestyle='--')
    ax.set_ylim(0, 1.1)
    ax.set(xlabel='',
           title='Relative performance')
    ax.legend(loc='lower right')

    # ax.grid()
    
    plt.show()

plot_comparison()
