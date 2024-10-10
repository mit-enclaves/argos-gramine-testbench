import os
import numpy as np
import matplotlib.pyplot as plt

NATIVE_PATH = "data-asplos/native/"
SGX_PATH = "data-asplos/gramine-sgx/"
GRAMINE_TYCHE_PATH = "data-asplos/gramine-tyche/"
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
    return data

sgx_hyper = parse_wrk(SGX_PATH + HYPER, REQUESTS_SECS)
tyche_gramine_hyper = parse_wrk(GRAMINE_TYCHE_PATH + HYPER, REQUESTS_SECS)

print(f"SGX:   {np.mean(sgx_hyper):.2f} +/- {np.std(sgx_hyper):.2f} Req/Sec")
print(f"Tyche: {np.mean(tyche_gramine_hyper):.2f} +/- {np.std(tyche_gramine_hyper):.2f} Req/Sec")
print(f"  Tyche is {np.mean(tyche_gramine_hyper) / np.mean(sgx_hyper):.2f}x faster than SGX")


lighttpd_sizes = ["100", "1K", "10K", "100K", "1M", "10M"]
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
    lighttpd_gramine_sgx = get_lighttpd_data(SGX_PATH, BYTES_SECS)
    lighttpd_gramine_tyche = get_lighttpd_data(GRAMINE_TYCHE_PATH, BYTES_SECS)
    lighttpd_themis_vm = get_lighttpd_data(THEMIC_VM_PATH, BYTES_SECS)
    # lighttpd_themis_conf = get_lighttpd_data(THEMIS_CONF_PATH, BYTES_SECS)
    lighttpd_tyche = get_lighttpd_data(TYCHE_PATH, BYTES_SECS)
    
    native = get_mean_std(lighttpd_native)
    gramine_sgx = get_mean_std(lighttpd_gramine_sgx)
    gramine_tyche = get_mean_std(lighttpd_gramine_tyche)
    themis_vm = get_mean_std(lighttpd_themis_vm)
    tyche = get_mean_std(lighttpd_tyche)
    # themis_conf = get_mean_std(lighttpd_themis_conf)

    fig, ax = plt.subplots()
    
    # Plot the bars
    width = 0.18
    x = np.arange(len(lighttpd_sizes))

    def plot_bar(data, shift, label):
        val = [x[0] for x in data]
        err = [x[1] for x in data]
        ax.bar(x + shift, val, width, label=label)
        ax.errorbar(x + shift, val, yerr = err, fmt='', linestyle='None',)

    plot_bar(native     ,   - 2 * width, "Linux Native")
    plot_bar(gramine_sgx,   - 1 * width, "Gramine SGX")
    plot_bar(tyche,         - 0 * width, "Tyche")
    plot_bar(gramine_tyche, + 1 * width, "Gramine Tyche")
    plot_bar(themis_vm,     + 2 * width, "Tyche VM")
    # plot_bar(themis_conf , + 2 * width, "Tyche CVM")

    plt.xticks(x, lighttpd_sizes)
    ax.set(xlabel='HTTP payload size (bytes)', ylabel='Relative MiB/s',
           title='lighttpd HTTP throughput')
    ax.legend(loc='lower right')

    # ax.grid()
    
    plt.show()


# plot_relative_reqsec_bar()
plot_throughput_bars()
