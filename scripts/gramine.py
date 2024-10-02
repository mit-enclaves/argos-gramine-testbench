import os
import numpy as np
import matplotlib.pyplot as plt

SGX_PATH = "data-asplos/gramine-sgx/"
TYCHE_PATH = "data-asplos/gramine-tyche/"
HYPER = "hyper.txt"

def parse_wrk(path: str):
    data = []
    with open(path, 'r') as file:
        for line in file:
            if not line.startswith("Requests/sec:"):
                continue

            req_per_sec = float(line.split()[1])
            data.append(req_per_sec)

            # We keep at most 10 samples
            if len(data) >= 10:
                break
    if len(data) < 10:
        print(f"WARNING: less than 10 samples in {path}")
    return data

sgx_hyper = parse_wrk(SGX_PATH + HYPER)
tyche_hyper = parse_wrk(TYCHE_PATH + HYPER)

print(f"SGX:   {np.mean(sgx_hyper):.2f} +/- {np.std(sgx_hyper):.2f} Req/Sec")
print(f"Tyche: {np.mean(tyche_hyper):.2f} +/- {np.std(tyche_hyper):.2f} Req/Sec")
print(f"  Tyche is {np.mean(tyche_hyper) / np.mean(sgx_hyper):.2f}x faster than SGX")


lighttpd_sizes = ["100", "1K", "10K", "100K", "1M", "10M"]
def get_lighttpd_data(folder_path: str):
    lighttpd_data = []
    for size in lighttpd_sizes:
        data = parse_wrk(SGX_PATH + "lighttpd-" + size + ".txt")
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

def plot_bar():
    lighttpd_gramine_sgx = get_lighttpd_data(SGX_PATH)
    lighttpd_gramine_tyche = get_lighttpd_data(TYCHE_PATH)
    
    gramine_sgx = normalize_lighttpd(lighttpd_gramine_sgx, lighttpd_gramine_sgx)
    gramine_tyche = normalize_lighttpd(lighttpd_gramine_sgx, lighttpd_gramine_sgx)
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

plot_bar()
