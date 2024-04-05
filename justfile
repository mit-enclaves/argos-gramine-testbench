ip-addr  := "128.178.116.218"
tcp-port := "6379"
tls-port := "6380"

# Print the list of commands
help:
	@just --list --unsorted

# Run redis benchmark
redis-benchmark:
    redis-benchmark -h {{ip-addr}} -p {{tcp-port}} -c 1 -n 10000 --csv > tmp/redis-benchmark.csv

# Run memtier_benchmark
memtier-benchmark:
    memtier_benchmark --host {{ip-addr}} -p {{tls-port}} --tls --tls-skip-verif --threads=1 --clients=1 --requests=10000 --json-out-file=tmp/memtier-benchmark.json

# The following line gives highlighting on vim
# vim: set ft=make :
