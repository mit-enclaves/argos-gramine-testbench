This repository is a fork of [Tyche Bench](https://github.com/epfl-dcsl/tyche-bench).

# Argos Gramine Testbench

This repository contains scripts and benchmarks for runing Argos with Gramine.

# General Setup

The justfile provides recipes to install dependencies and compile all the necessary
tools to run gramine and lkvm benchmarks.

Cloned repositories end up in `ROOT_CLONES=git-repos`, while folders to be copied
to the argos machine are populated in `INSTALL_FOLDER=to-copy`.

## just setup-all ARGOS_MONITOR

args: ARGOS_MONITOR=path/to/argos-monitor/folder

Download, compile, and copy gramine and its benchmarks.
Download, compile, and copy executable for the modified lkvm.
Download, compile, and copy memtier_benchmark and wrk2.

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

The `my_bin` folder content can be copied anywhere on the machine as long as
it is in the `$PATH`.

The `gramine` folder needs to be copied at `/` on the machine.

The `gramine-benchmark` can be placed anywhere.

# Running benchmarks

## Commands

The main command for gramine benchmarks is:

```
just setup-gramine ARGOS_MONITOR
```

This will download and compile gramine and its benchmarks.
It then creates folders to be copied to your dev machine in `to-copy`.

This is a meta command that actually calls the following ones:

```
  @just create-setup-target               # Create target folders
  @just download-gramine                  # Clone gramine
  @just compile-gramine {{ARGOS_MONITOR}}   # Compile gramine
  @just compile-gramine-benchmarks        # Compile individual benchmarks
  @just copy-gramine-binaries             # Copy all binaries to to-copy

```

## Setting up your machine

To properly run graming on your machine, you will need to move some of the content
from `to-copy` to your machine.

The `to-copy/gramine` should be copied to `/gramine`.
It is path sensitive and cannot be placed randomly.

The `to-copy/my_bin` contains utility binaries (lkvm, wrk, memtier_benchmark).
The folder or its binaries can be copied anywhere on the target machine as long as
their containing folder is within the `PATH`.
For example, I put it inside `/argos/my_bin` and make sure that my bashrc ends with:

```
export PATH=/argos/my_bin:$PATH
```

The `to-copy/gramine-benchmarks` contains the compiled benchmarks and utilities to
run pre-defined workloads.

## Running

The `to-copy/gramine-benchmarks/Makefile` is copied from config/Makefile.gramine.
It allows to run gramine benchmarks easily by spawning both client and server.
It stores the results in the same folder under `results/NAME_OF_THE_APP/`.
If the `TYCHE=1` environment variable is set, it runs with `gramine-tyche`.
Otherwise, it runs the benchmarks with `gramine-direct` (linux version).

# Gramine Benchmarks

The justfile clones (git) and compiles the argos gramine version.

As gramine is very sensitive to absolute paths and to enable compiling locally
and then copying binaries to, e.g., a dev machine, gramine install directory is located
in `/gramine/`, which is copied into `to-copy/gramine`.

The gramine binaries and libraries (including python) are generated into `/gramine`.

The binaries used by applications that are path sensitive are installed inside `/gramine/utils`.
(See Notes on ligttpd).

Benchmarks are compiled and populated inside `to-copy/gramine-benchmarks`.

## Benchmarks

- `helloworld`: simple C helloworld.
- `hellocpp`: simple C++ helloworld.
- `seal`: SEAL benchmark.
- `sealPIR`: SEAL PIR benchmark.
- `sealAPSI`: SEAL APSI benchmark.