from argparse import Action, Namespace
from typing import (List)

from data_manager.switch_config import SwitchConfigCLI
from switch import SwitchChip


class EraseConfigCLI(SwitchConfigCLI):
    """
    The "erase" action that removes all stored items from the EEPROM memory.
    """
    def __init__(self, subparsers: Action, switch: SwitchChip) -> None:
        super().__init__(subparsers, switch)

        self._subparser = self._subparsers.add_parser(
            "erase",
            help="Erase all configuration",
        )
        self._subparser.set_defaults(execute=self.apply)

    def apply(self, args: Namespace) -> SwitchConfigCLI:
        return self

    def create_configuration(self) -> List[List[int]]:
        return [[101, 0, 0, 0]]
