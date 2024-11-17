"""Command line interface."""

from glob import glob
from pathlib import Path

from libcli import BaseCLI

from fidelity.fidelity import Fidelity

__all__ = ["FidelityCLI"]


class FidelityCLI(BaseCLI):
    """Command line-interface."""

    config = {
        "config-file": "~/.fidelity.toml",
        # distribution name, not importable package name
        "dist-name": "rlane-fidelity",
    }

    def init_parser(self) -> None:
        """Initialize argument parser."""

        self.ArgumentParser(
            prog=__package__,
            description=self.dedent(
                """
    Process downloaded Fidelity history files.
                """
            ),
        )

    def add_arguments(self) -> None:
        """Add arguments to parser."""

        group = self.parser.add_argument_group("Datafile options")

        arg = group.add_argument(
            "--use-datafiles",
            action="store_true",
            help="Process the `CSV` files defined under `datafiles` in the config file",
        )
        self.add_default_to_help(arg, self.parser)

        group.add_argument(
            "FILES",
            nargs="*",
            help="The `CSV` file(s) to process",
        )

        group = self.parser.add_argument_group(
            "Configuration File",
            self.dedent(
                """
    The configuration file defines these elements:

        `datafiles` (str):  Points to the `CSV` files to process. May
                            begin with `~`, and may contain wildcards.
                """
            ),
        )

    def main(self) -> None:
        """Command line interface entry point (method)."""

        # Read all `csv` files on the command line within the date range.
        fidelity = Fidelity()  # self.config, self.options)
        #
        if self.options.use_datafiles and (datafiles := self.config.get("datafiles")):
            files = glob(str(Path(datafiles).expanduser()))
        else:
            files = self.options.FILES
        #
        fidelity.read_input_files(files)

        fidelity.print_history_report()
        fidelity.print_symbol_report()
        fidelity.print_position_report()


def main(args: list[str] | None = None) -> None:
    """Command line interface entry point (function)."""
    FidelityCLI(args).main()
