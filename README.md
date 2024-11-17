### fidelity - Process Fidelity transaction files

#### Usage
    fidelity [--use-datafiles] [-h] [-v] [-V] [--config FILE]
             [--print-config] [--print-url] [--completion [SHELL]]
             [FILES ...]
    
Process downloaded Fidelity history files.

#### Datafile options
    --use-datafiles     Process the `CSV` files defined under `datafiles` in
                        the config file (default: `False`).
    FILES               The `CSV` file(s) to process.

#### Configuration File
  The configuration file defines these elements:
  
      `datafiles` (str):  Points to the `CSV` files to process. May
                          begin with `~`, and may contain wildcards.

#### General options
    -h, --help          Show this help message and exit.
    -v, --verbose       `-v` for detailed output and `-vv` for more detailed.
    -V, --version       Print version number and exit.
    --config FILE       Use config `FILE` (default: `~/.fidelity.toml`).
    --print-config      Print effective config and exit.
    --print-url         Print project url and exit.
    --completion [SHELL]
                        Print completion scripts for `SHELL` and exit
                        (default: `bash`).
