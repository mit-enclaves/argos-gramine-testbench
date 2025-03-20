This repository is a fork of [Tyche Bench](https://github.com/epfl-dcsl/tyche-bench).

# Argos Gramine Testbench

This repository contains scripts and benchmarks for runing Argos with Gramine.

**NOTE**: To use gramine, you must use the `argos_gramine` branch of [`argos_monitor`](https://github.com/mit-enclaves/argos-monitor/tree/argos_gramine).

# General Setup

```bash
git submodule update --init --recursive
```

The justfile provides recipes to install dependencies and compile all the necessary
tools to run argos+gramine benchmarks.

Folders to be copied to the argos machine are populated in `INSTALL_FOLDER=to-copy`.

```bash
just setup-all ARGOS_MONITOR
```
args: ARGOS_MONITOR=path/to/argos-monitor/folder

If everything goes well, you should have the following content in `to-copy`:

```
to-copy
├── gramine
│   ├── gramine
│   ├── gramine-argv-serializer
│   ├── gramine-direct
│   ├── gramine-gen-depend
│   ├── gramine-manifest
│   ├── gramine-manifest-check
│   ├── gramine-tyche
│   ├── include
│   ├── lib
│   └── utils
└── gramine-benchmarks
    ├── common_tools
    ├── helloworld
    ├── hellocpp
    ├── seal
    ├── sealAPSI
    ├── sealPIR
    └── Makefile
```

The `gramine` folder needs to be copied at `/` on the machine.

The `gramine-benchmark` can be placed anywhere.

# Running benchmarks

## Commands

The main command for gramine benchmarks is:

```
just setup-gramine ARGOS_MONITOR
```

This will compile gramine and its benchmarks.
It then creates folders to be copied to your dev machine in `to-copy`.

This is a meta command that actually calls the following ones:

```
  @just create-setup-target               # Create target folders
  @just compile-gramine {{ARGOS_MONITOR}}   # Compile gramine
  @just compile-gramine-benchmarks        # Compile individual benchmarks
  @just copy-gramine-binaries             # Copy all binaries to to-copy
  @just setup-seal                        # Compiles and copies binaries for SEAL apps

```

## Setting up your machine

To properly run gramine on your machine, you will need to move some of the content
from `to-copy` to your machine.

The `to-copy/gramine` should be copied to `/gramine`.
It is path sensitive and cannot be placed randomly.

The `to-copy/gramine-benchmarks` contains the compiled benchmarks and utilities to
run pre-defined workloads.

## Running Gramine SEAL benchmarks

After properly copying the folders from the above section, navigate to a benchmark folder, e.g. `~/gramine-benchmarks/seal`.

Run the SEAL benchmark under gramine with the following command:

`$ sudo /gramine/gramine-tyche sealexamples`

Where `sealexamples` is base name of the `.manifest` file in the current folder.

## Benchmarks

- `helloworld`: simple C helloworld.
- `hellocpp`: simple C++ helloworld.
- `seal`: SEAL benchmark.
- `sealPIR`: SEAL PIR benchmark.
- `sealAPSI`: SEAL APSI benchmark.