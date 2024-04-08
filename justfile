ip-addr  := "128.178.116.181"
tcp-port := "1234"
tls-port := "1234"
n_reqs   := "10000"

# Print the list of commands
help:
	@just --list --unsorted

# Run redis benchmark
redis-benchmark:
    redis-benchmark -h {{ip-addr}} -p {{tcp-port}} -c 1 -n {{n_reqs}} --csv > tmp/redis-benchmark.csv

# Run memtier_benchmark with TLS
memtier-benchmark-tls:
    memtier_benchmark --host {{ip-addr}} -p {{tls-port}} --tls --tls-skip-verif --threads=1 --clients=1 --requests={{n_reqs}}  --tls --tls-skip-verif --json-out-file=tmp/memtier-benchmark-tls.json

# Run memtier_benchmark
memtier-benchmark:
    memtier_benchmark --host {{ip-addr}} -p {{tcp-port}} --threads=1 --clients=1 --requests={{n_reqs}} --json-out-file=tmp/memtier-benchmark.json


# The following line gives highlighting on vim
# vim: set ft=make :
