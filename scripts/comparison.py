import os
import numpy as np
import matplotlib.pyplot as plt

SGX_PATH = "data-asplos/gramine-sgx/"
GRAMINE_TYCHE_PATH = "data-asplos/gramine-tyche/"
THEMIS_CONF_PATH = "data-asplos/themis-conf/"
TYCHE_PATH = "data-asplos/tyche/"

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

labels = ["hyper", "lighttpd"]
sgx = []
themis_conf = []
tyche_gramine = []

sgx.append(parse_wrk(SGX_PATH + HYPER, REQUESTS_SECS))
themis_conf.append(parse_wrk(THEMIS_CONF_PATH + HYPER, REQUESTS_SECS))
tyche_gramine.append(parse_wrk(GRAMINE_TYCHE_PATH + HYPER, REQUESTS_SECS))

print(f"SGX:           {sgx[0][0]:.2f} +/- {sgx[0][0]:.2f} Req/Sec")
print(f"Gramine Tyche: {tyche_gramine[0][0]:.2f} +/- {tyche_gramine[0][0]:.2f} Req/Sec")
print(f"THEMIS CVM:    {themis_conf[0][0]:.2f} +/- {themis_conf[0][0]:.2f} Req/Sec")
print(f"  Tyche is {tyche_gramine[0][0] / sgx[0][0]:.2f}x faster than SGX")

sgx.append(parse_wrk(SGX_PATH + LIGHTTPD, BYTES_SECS))
themis_conf.append(parse_wrk(THEMIS_CONF_PATH + LIGHTTPD, BYTES_SECS))
tyche_gramine.append(parse_wrk(GRAMINE_TYCHE_PATH + LIGHTTPD, BYTES_SECS))

def make_relative(ref, data):
    scaled = []
    for i in range(len(ref)):
        r = ref[i]
        d = data[i]
        scaled.append((d[0]/r[0], d[1]/r[0]))
    return scaled


themis_conf = make_relative(sgx, themis_conf)
tyche_gramine = make_relative(sgx, tyche_gramine)
sgx = make_relative(sgx, sgx)

print(themis_conf)
print(tyche_gramine)
print(sgx)

def plot_comparison():

    fig, ax = plt.subplots()
    
    # Plot the bars
    width = 0.25
    x = np.arange(len(labels))

    ax.bar(x - width, [x[0] for x in sgx], width, label='Gramine SGX')
    ax.bar(x + 0,     [x[0] for x in tyche_gramine], width, label='Gramine Anon')
    ax.bar(x + width, [x[0] for x in themis_conf], width, label='Anon CVM')

    plt.xticks(x, labels)
    ax.axhline(y=1, color='black', linestyle='--')
    ax.set_ylim(0, 2)
    ax.set(xlabel='',
           title='Relative performance')
    ax.legend(loc='lower right')

    # ax.grid()
    
    plt.show()

plot_comparison()
