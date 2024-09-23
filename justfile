ip-addr  := "128.178.116.124"
tcp-port := "1234"
tls-port := "1234"
n_reqs   := "10000"


ROOT_CLONES := "git-repos"
INSTALL_FOLDER := "to-copy"
GRAMINE_INSTALL := "/gramine/"
GRAMINE_UTILS := "/gramine/utils/"
GRAMINE_BENCHMARKS := "to-copy/gramine-benchmarks/"
CUSTOM_BINARIES := "to-copy/my_bin/"


## ————————————————————————————— Setup for all —————————————————————————————— //
# TYCHE_DEVEL is the path to the tyche-devel folder.
# It is required for gramine.

setup-all TYCHE_DEVEL:
  @just install-dependencies
  @just setup-gramine {{TYCHE_DEVEL}}
  @just setup-lkvm
  @just setup-memtier
  @just setup-wrk

## ————————————————————————————— Gramine setup —————————————————————————————— //
setup-gramine TYCHE_DEVEL:
  @just create-setup-target
  @just download-gramine
  @just recompile-gramine {{TYCHE_DEVEL}}

recompile-gramine TYCHE_DEVEL:
  @just compile-gramine {{TYCHE_DEVEL}}
  @just compile-gramine-benchmarks
  @just copy-gramine-binaries

download-gramine:
  #!/usr/bin/env bash
  mkdir -p {{ROOT_CLONES}} 
  rm -rf {{ROOT_CLONES}}/gramine 2>/dev/null
  git clone git@github.com:epfl-dcsl/gramine.git --branch tyche {{ROOT_CLONES}}/gramine
  
compile-gramine TYCHE_DEVEL:
  #!/usr/bin/env bash
  ABSOLUTE=$(realpath "{{TYCHE_DEVEL}}")
  sudo mkdir -p {{GRAMINE_INSTALL}}
  sudo chown $USER:$USER {{GRAMINE_INSTALL}}
  sudo chmod 777 {{GRAMINE_INSTALL}}
  TYCHE_ROOT=$ABSOLUTE TARGET={{GRAMINE_INSTALL}} make -C {{ROOT_CLONES}}/gramine 

compile-gramine-benchmarks:
  @just delete-gramine-benchmarks
  @just compile-gramine-benchmark helloworld
  @just compile-gramine-benchmark redis
  @just compile-gramine-benchmark lighttpd
  @just compile-gramine-benchmark rust
  @just compile-gramine-benchmark sqlite
  @just disable-debug-gramine-benchmarks

delete-gramine-benchmarks:
  #!/usr/bin/env bash
  if [ -e {{GRAMINE_BENCHMARKS}} ]; then
    sudo rm -rf {{GRAMINE_BENCHMARKS}};
  fi

# Compile a specific BENCHMARK
compile-gramine-benchmark BENCHMARK:
  #!/usr/bin/env bash
  export INSTALL_DIR={{GRAMINE_UTILS}}/{{BENCHMARK}}/
  export PATH={{GRAMINE_INSTALL}}:$PATH
  export PYTHONPATH={{GRAMINE_INSTALL}}/lib/python3.10/site-packages/
  make -C {{ROOT_CLONES}}/gramine/CI-Examples/{{BENCHMARK}}
  mkdir -p {{GRAMINE_BENCHMARKS}} 
  cp -r {{ROOT_CLONES}}/gramine/CI-Examples/{{BENCHMARK}} {{GRAMINE_BENCHMARKS}}/

disable-debug-gramine-benchmarks:
  #!/usr/bin/env bash
  find {{GRAMINE_BENCHMARKS}} -type f -name "*.manifest" -exec sed -i 's/sgx\.debug = true/sgx\.debug = false/g' {} +
  find {{GRAMINE_BENCHMARKS}} -type f -name "*.manifest" -exec sed -i 's/debug = true/debug = false/g' {} +


copy-gramine-binaries:
  #!/usr/bin/env bash
  sudo rm -rf {{INSTALL_FOLDER}}/gramine
  sudo cp -r {{GRAMINE_INSTALL}} {{INSTALL_FOLDER}}/gramine
  sudo cp -r {{ROOT_CLONES}}/gramine/CI-Examples/common_tools {{GRAMINE_BENCHMARKS}}/common_tools
  cp config/Makefile.gramine {{GRAMINE_BENCHMARKS}}/Makefile

## ——————————————————————————————— lkvm setup ——————————————————————————————— //

setup-lkvm:
  @just create-setup-target
  @just download-lkvm
  @just compile-lkvm

download-lkvm:
  #!/usr/bin/env bash
  git clone git@github.com:epfl-dcsl/tyche-kvmtool.git {{ROOT_CLONES}}/lkvm

compile-lkvm:
  #!/usr/bin/env bash
  make -C {{ROOT_CLONES}}/lkvm
  mkdir -p {{CUSTOM_BINARIES}}
  cp {{ROOT_CLONES}}/lkvm/lkvm {{CUSTOM_BINARIES}} 

## ————————————————————————————— Memtier setup —————————————————————————————— //

setup-memtier:
  @just download-memtier
  @just compile-memtier
  @just install-memtier

download-memtier:
  #!/usr/bin/env bash
  git clone git@github.com:RedisLabs/memtier_benchmark.git --branch 2.1.1 {{ROOT_CLONES}}/memtier_benchmark

compile-memtier:
  #!/usr/bin/env bash
  cd {{ROOT_CLONES}}/memtier_benchmark
  autoreconf -ivf
  ./configure
  make

install-memtier:
  #!/usr/bin/env bash
  mkdir -p {{CUSTOM_BINARIES}}
  cp {{ROOT_CLONES}}/memtier_benchmark/memtier_benchmark {{CUSTOM_BINARIES}}

## —————————————————————————————————— Wrk2 —————————————————————————————————— //

setup-wrk:
  @just download-wrk
  @just compile-wrk
  @just install-wrk

download-wrk:
  #!/usr/bin/env bash
  git clone git@github.com:giltene/wrk2.git {{ROOT_CLONES}}/wrk2

compile-wrk:
  #!/usr/bin/env bash
  cd {{ROOT_CLONES}}/wrk2
  make

install-wrk:
  #!/usr/bin/env bash
  cp {{ROOT_CLONES}}/wrk2/wrk {{CUSTOM_BINARIES}}/wrk

## —————————————————————————————— Dependencies —————————————————————————————— //

# Create the folders to clone git repos and to produce final results.
create-setup-target:
  mkdir -p {{ROOT_CLONES}}
  mkdir -p {{INSTALL_FOLDER}}

install-dependencies:
  sudo apt-get install -y build-essential \
    autoconf bison gawk nasm ninja-build pkg-config python3 python3-click \
    python3-jinja2 python3-pip python3-pyelftools python3-voluptuous wget \
    libunwind8 musl-tools python3-pytest libgmp-dev libmpfr-dev libmpc-dev \
    libisl-dev cmake libprotobuf-c-dev protobuf-c-compiler \
    protobuf-compiler python3-cryptography python3-pip python3-protobuf \
    sqlite3 automake libpcre3-dev libevent-dev zlib1g-dev libssl-dev wget
  sudo python3 -m pip install 'meson>=0.56' 'tomli>=1.1.0' 'tomli-w>=0.4.0'

## ————————————————————————————————— Helper ————————————————————————————————— //

# Print the list of commands
help:
	@just --list --unsorted

## ——————————————————————————— Running benchmarks ——————————————————————————— //

# Run redis benchmark
redis-benchmark:
    redis-benchmark -h {{ip-addr}} -p {{tcp-port}} -c 1 -n {{n_reqs}} --csv > tmp/redis-benchmark.csv

# Run memtier_benchmark with TLS
memtier-benchmark-tls:
    memtier_benchmark --host {{ip-addr}} -p {{tls-port}} --tls --tls-skip-verif --threads=1 --clients=1 --requests={{n_reqs}}  --tls --tls-skip-verif --json-out-file=tmp/memtier-benchmark-tls.json

# Run memtier_benchmark
memtier-benchmark:
    memtier_benchmark --host {{ip-addr}} -p {{tcp-port}} --threads=1 --clients=1 --requests={{n_reqs}} --json-out-file=tmp/memtier-benchmark.json

tokio-benchmark:
	wrk -t12 -c400 -d120s http://{{ip-addr}}:8000

lighttpd-benchmark:
	wrk -t12 -c400 -d120s http://{{ip-addr}}:8003

# The following line gives highlighting on vim
# vim: set ft=make :
