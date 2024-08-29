# Tyche Bench

This repository contains scripts and benchmarks results for Tyche

- redis version: 7.0.15
- musl libc version: 1.2.3

# General Setup

The justfile provides recipes to install dependencies and compile all the necessary
tools to run gramine and lkvm benchmarks.

Cloned repositories end up in `ROOT_CLONES=git-repos`, while folders to be copied
to the tyche machine are populated in `INSTALL_FOLDER=to-copy`.

## just setup-all TYCHE_DEVEL

args: TYCHE_DEVEL=path/to/tyche_devel/folder

Download, compile, and copy gramine and its benchmarks.
Download, compile, and copy executable for the modified lkvm.

# Gramine Benchmarks

The justfile clones (git) and compiles the tyche gramine version.

As gramine is very sensitive to absolute paths and to enable compiling locally
and then copying binaries to, e.g., a dev machine, gramine install directory is located
in `/gramine/`, which is copied into `to-copy/gramine`.

The gramine binaries and libraries (including python) are generated into `/gramine`.

The binaries used by applications that are path sensitive are installed inside `/gramine/utils`.
(See Notes on ligttpd).

Benchmarks are compiled and populated inside `to-copy/gramine-benchmarks`.


## Benchmarks

- `helloworld`: simple C helloworld.
- `redis`: unmodified redis-server.
- `lighttpd`: a C http server.
- `rust`: rust hyper http server.
- `sqlite`: the unmodified sqlite3 database.

**Notes**: lighttpd is installed from source and the binary is generated into `/gramine/utils`.
This avoids struggling to generate a portable manifest for the application.

# LKVM

The [lkvm fork](git@github.com:epfl-dcsl/tyche-kvmtool.git) is a modified version of lkvm.
The justfile clones the repository inside `git-repos`, compiles it and copies the resulting
binary into `to-copy/lkvm-bin`.

