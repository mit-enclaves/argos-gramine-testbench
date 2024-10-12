import os
import numpy as np
import matplotlib.pyplot as plt
import colors
import utils

NATIVE_PATH = "data-asplos/native/"
NATIVE_VM_PATH = "data-asplos/native-vm/"
SGX_PATH = "data-asplos/gramine-sgx/"
GRAMINE_TYCHE_PATH = "data-asplos/gramine-tyche/"
THEMIS_CONF_GRAMINE_PATH = "data-asplos/themis-conf-gramine/"
THEMIS_CONF_PATH = "data-asplos/themis-conf/"
THEMIC_VM_PATH = "data-asplos/themis-vm/"
TYCHE_PATH = "data-asplos/tyche/"
HYPER = "hyper.txt"

REQUESTS_SECS = "Requests/sec:"
BYTES_SECS = "Transfer/sec:"

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
    remove_worst(data, lower_is_better=False)
    return data

sgx_hyper = parse_wrk(SGX_PATH + HYPER, REQUESTS_SECS)
tyche_gramine_hyper = parse_wrk(GRAMINE_TYCHE_PATH + HYPER, REQUESTS_SECS)

print(f"SGX:   {np.mean(sgx_hyper):.2f} +/- {np.std(sgx_hyper):.2f} Req/Sec")
print(f"Tyche: {np.mean(tyche_gramine_hyper):.2f} +/- {np.std(tyche_gramine_hyper):.2f} Req/Sec")
print(f"  Tyche is {np.mean(tyche_gramine_hyper) / np.mean(sgx_hyper):.2f}x faster than SGX")


lighttpd_sizes = ["100", "1K", "10K", "100K", "1M"] # , "10M"
def get_lighttpd_data(folder_path: str, label: str):
    lighttpd_data = []
    for size in lighttpd_sizes:
        data = parse_wrk(folder_path + "lighttpd-" + size + ".txt", label)
        lighttpd_data.append(data)
    return lighttpd_data

def normalize_lighttpd(reference, data):
    normalized_list = []
    for i in range(len(reference)):
        mean = np.mean(reference[i])
        normalized = data[i] / mean
        normalized_list.append((
            float(np.mean(normalized)),
            float(np.std(normalized)),
            float(np.mean(data[i]))
        ))
    return normalized_list

def get_mean_std(data):
    cleaned = []
    for item in data:
        cleaned.append((float(np.mean(item)), float(np.std(item))))
    return cleaned

def plot_relative_reqsec_bar():
    lighttpd_gramine_sgx = get_lighttpd_data(SGX_PATH, REQUESTS_SECS)
    lighttpd_gramine_tyche = get_lighttpd_data(GRAMINE_TYCHE_PATH, REQUESTS_SECS)
    
    gramine_sgx = normalize_lighttpd(lighttpd_gramine_sgx, lighttpd_gramine_sgx)
    gramine_tyche = normalize_lighttpd(lighttpd_gramine_sgx, lighttpd_gramine_tyche)
    print(gramine_sgx)

    fig, ax = plt.subplots()
    
    # Plot the bars
    width = 0.35
    x = np.arange(len(lighttpd_sizes))

    bars_gramine_sgx = ax.bar(x - width/2, [x[0] for x in gramine_sgx], width, label='Gramine SGX')
    bars_gramine_tyche = ax.bar(x + width/2, [x[0] for x in gramine_tyche], width, label='Gramine Anon')

    plt.xticks(x, lighttpd_sizes)
    ax.axhline(y=1, color='black', linestyle='--')
    ax.set_ylim(0, 1.18)
    ax.set(xlabel='HTTP payload size (bytes)', ylabel='Relative requests/secondes',
           title='lighttpd HTTP throughput')
    ax.legend(loc='lower right')

    def add_values(bars, scores):
        for i in range(len(scores)):
            bar = bars[i]
            score = scores[i][2]
            ax.annotate(f'{int(score)}',
                        xy=(bar.get_x() + bar.get_width() / 2, 1.02),
                        ha='center', va='bottom', rotation=90)
    add_values(bars_gramine_sgx, gramine_sgx)
    add_values(bars_gramine_tyche, gramine_tyche)

    # ax.grid()
    
    plt.show()

def plot_throughput_bars():
    lighttpd_native = get_lighttpd_data(NATIVE_PATH, BYTES_SECS)
    lighttpd_native_vm = get_lighttpd_data(NATIVE_VM_PATH, BYTES_SECS)
    lighttpd_gramine_sgx = get_lighttpd_data(SGX_PATH, BYTES_SECS)
    lighttpd_gramine_tyche = get_lighttpd_data(GRAMINE_TYCHE_PATH, BYTES_SECS)
    lighttpd_themis_vm = get_lighttpd_data(THEMIC_VM_PATH, BYTES_SECS)
    lighttpd_themis_conf = get_lighttpd_data(THEMIS_CONF_PATH, BYTES_SECS)
    lighttpd_themis_conf_gramine = get_lighttpd_data(THEMIS_CONF_GRAMINE_PATH, BYTES_SECS)
    lighttpd_tyche = get_lighttpd_data(TYCHE_PATH, BYTES_SECS)
    
    native = get_mean_std(lighttpd_native)
    native_vm = get_mean_std(lighttpd_native_vm)
    gramine_sgx = get_mean_std(lighttpd_gramine_sgx)
    gramine_tyche = get_mean_std(lighttpd_gramine_tyche)
    themis_vm = get_mean_std(lighttpd_themis_vm)
    tyche = get_mean_std(lighttpd_tyche)
    themis_conf = get_mean_std(lighttpd_themis_conf)
    themis_conf_gramine = get_mean_std(lighttpd_themis_conf_gramine)


    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    
    # colors
    ctyche = colors.get_tyche()
    cnative = colors.get_native()

    # Plot the bars
    width = 0.11
    x = np.arange(len(lighttpd_sizes))

    def plot_bar(data, shift, label, color, hatch=""):
        val = [x[0] for x in data]
        err = [x[1] for x in data]
        ax.bar(x + shift, val, width, label=label, edgecolor='black', color=color, hatch=hatch)
        ax.errorbar(x + shift, val, yerr = err, fmt='', linestyle='None', color='black')

    plot_bar(native     ,         - 3.5 * width, "Native", cnative[0])
    plot_bar(native_vm  ,         - 2.5 * width, "Native VM", cnative[1], hatch='..')
    plot_bar(gramine_sgx,         - 1.5 * width, "SGX enclave", cnative[2], hatch='//')
    plot_bar(tyche,               - 0.5 * width, "TD0", ctyche[0])
    plot_bar(themis_vm,           + 0.5 * width, "TD1 VM", ctyche[1], hatch="..")
    plot_bar(themis_conf,         + 1.5 * width, "TD1 CVM", ctyche[2], hatch="\\\\")
    plot_bar(gramine_tyche,       + 2.5 * width, "TD1 enclave", ctyche[3], hatch='//')
    plot_bar(themis_conf_gramine, + 3.5 * width, "TD2 enclave", ctyche[4], hatch='xx')

    plt.xticks(x, lighttpd_sizes)
    ax.set(xlabel='HTTP payload size (bytes)', ylabel='Relative MiB/s',
           title='lighttpd HTTP throughput')
    ax.legend(loc='lower right')

    utils.plot_or_save("lighttpd")


# plot_relative_reqsec_bar()
plot_throughput_bars()
