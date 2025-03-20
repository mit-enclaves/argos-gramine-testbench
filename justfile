ROOT_CLONES := "git-repos"
INSTALL_FOLDER := "to-copy"
GRAMINE_INSTALL := "/gramine/"
GRAMINE_UTILS := "/gramine/utils/"
GRAMINE_BENCHMARKS := "to-copy/gramine-benchmarks/"
CUSTOM_BINARIES := "to-copy/my_bin/"

## ————————————————————————————— Setup for all —————————————————————————————— //
# ARGOS_MONITOR is the path to the argos-monitor folder.
# It is required for gramine.

setup-all ARGOS_MONITOR:
  @just install-dependencies
  @just setup-gramine {{ARGOS_MONITOR}}
  @just setup-lkvm
  @just setup-memtier
  @just setup-wrk

## ————————————————————————————— Gramine setup —————————————————————————————— //
setup-gramine ARGOS_MONITOR:
  @just create-setup-target
  @just download-gramine
  @just recompile-gramine {{ARGOS_MONITOR}}
  @just setup-seal

recompile-gramine ARGOS_MONITOR:
  @just compile-gramine {{ARGOS_MONITOR}}
  @just compile-gramine-benchmarks
  @just copy-gramine-binaries

download-gramine:
  #!/usr/bin/env bash
  mkdir -p {{ROOT_CLONES}}
  rm -rf {{ROOT_CLONES}}/gramine 2>/dev/null
  git clone https://github.com/mit-enclaves/argos-gramine.git --branch master {{ROOT_CLONES}}/gramine

compile-gramine ARGOS_MONITOR:
  #!/usr/bin/env bash
  ABSOLUTE=$(realpath "{{ARGOS_MONITOR}}")
  sudo mkdir -p {{GRAMINE_INSTALL}}
  sudo chown $USER:$USER {{GRAMINE_INSTALL}}
  TYCHE_ROOT=$ABSOLUTE TARGET={{GRAMINE_INSTALL}} make -C {{ROOT_CLONES}}/gramine 
  sudo chmod -R 777 {{GRAMINE_INSTALL}}

compile-gramine-benchmarks:
  @just delete-gramine-benchmarks
  @just compile-gramine-benchmark helloworld
  @just compile-gramine-benchmark hellocpp
  @just compile-gramine-benchmark seal
  @just compile-gramine-benchmark sealPIR
  @just compile-gramine-benchmark sealAPSI
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
  git clone https://github.com/epfl-dcsl/tyche-kvmtool.git {{ROOT_CLONES}}/lkvm

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

## ——————————————————————————— SEAL benchmarks ——————————————————————————— //

setup-seal:
  @just download-seal
  @just build-seal
  @just download-sealpir
  @just build-sealpir
  @just download-sealapsi
  @just build-sealapsi
  @just copy-seal-binaries

download-seal:
  #!/usr/bin/env bash
  mkdir -p {{ROOT_CLONES}}
  rm -rf {{ROOT_CLONES}}/SEAL 2>/dev/null
  git clone https://github.com/mit-enclaves/SEAL.git --branch no_tyche {{ROOT_CLONES}}/SEAL

build-seal:
  #!/usr/bin/env bash
  cd {{ROOT_CLONES}}/SEAL
  rm -rf build
  cmake -S . -DCMAKE_TOOLCHAIN_FILE=seal-toolchain.cmake -B build -DSEAL_BUILD_EXAMPLES=ON -DSEAL_USE_INTRIN=ON -DSEAL_USE_INTEL_HEXL=ON -DSEAL_THROW_ON_TRANSPARENT_CIPHERTEXT=OFF
  cmake --build build

download-sealpir:
  #!/usr/bin/env bash
  mkdir -p {{ROOT_CLONES}}
  rm -rf {{ROOT_CLONES}}/SealPIR 2>/dev/null
  git clone https://github.com/mit-enclaves/SealPIR.git --branch no_tyche {{ROOT_CLONES}}/SealPIR

build-sealpir:
  #!/usr/bin/env bash
  cd {{ROOT_CLONES}}/SealPIR
  cmake . -DCMAKE_TOOLCHAIN_FILE=seal-toolchain.cmake
  make

download-sealapsi:
  #!/usr/bin/env bash
  mkdir -p {{ROOT_CLONES}}
  rm -rf {{ROOT_CLONES}}/APSI 2>/dev/null
  git clone https://github.com/mit-enclaves/APSI.git --branch single_threaded {{ROOT_CLONES}}/APSI

build-sealapsi:
  #!/usr/bin/env bash
  cd {{ROOT_CLONES}}/APSI
  rm -rf build
  cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=../seal-toolchain.cmake -DAPSI_BUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Release -DAPSI_USE_LOG4CPLUS=OFF -DAPSI_USE_ZMQ=OFF
  make -C build -j$(nproc)

copy-seal-binaries:
  #!/usr/bin/env bash
  cp {{ROOT_CLONES}}/SEAL/build/bin/sealexamples {{GRAMINE_BENCHMARKS}}/seal/sealexamples
  cp {{ROOT_CLONES}}/SealPIR/bin/main {{GRAMINE_BENCHMARKS}}/sealPIR/sealexamples
  cp {{ROOT_CLONES}}/APSI/build/bin/integration_tests {{GRAMINE_BENCHMARKS}}/sealAPSI/sealAPSI
