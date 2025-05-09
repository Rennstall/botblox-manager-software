from typing import List, Optional, Type

from .config_writer import ConfigWriter, UARTWriter
from .fields import BitField, BitsField, ByteField, PortListField, ShortField
from .port import Port
from .register import MIIRegister, MIIRegisterAddress
from .switch import SwitchChip, SwitchFeature


class IP175G(SwitchChip[MIIRegisterAddress, MIIRegister, List[List[int]]]):
    """The Microchip IP175G chip used in Switchblox and Switchblox Nano."""

    def __init__(self, nano: bool = False) -> None:
        self._nano = nano
        super().__init__()

    def name(self) -> str:
        return "Switchblox Nano" if self._nano else "Switchblox"

    def _get_config_writer_type(self) -> Type[ConfigWriter]:
        return UARTWriter

    def _init_features(self) -> None:
        self._features = {
            SwitchFeature.TAGGED_VLAN,
            SwitchFeature.VLAN_TABLE,
            SwitchFeature.VLAN_MODE_OPTIONAL,
            SwitchFeature.VLAN_MODE_ENABLE,
            SwitchFeature.VLAN_MODE_STRICT,
            SwitchFeature.VLAN_FORCE,
            SwitchFeature.PER_PORT_VLAN_MODE,
            SwitchFeature.PER_PORT_VLAN_MODE_DISABLE,
            SwitchFeature.PER_PORT_VLAN_MODE_OPTIONAL,
            SwitchFeature.PER_PORT_VLAN_MODE_ENABLE,
            SwitchFeature.PER_PORT_VLAN_MODE_STRICT,
            SwitchFeature.PER_PORT_VLAN_FORCE,
            SwitchFeature.PER_PORT_VLAN_HEADER_ACTION,
        }

    def _init_ports(self) -> None:
        self._ports.append(Port("1", 2))
        self._ports.append(Port("2", 3))
        self._ports.append(Port("3", 4))
        if not self._nano:
            self._ports.append(Port("4", 6))
            self._ports.append(Port("5", 7))

    def _init_registers(self) -> None:
        self._add_register(MIIRegister(23, 0))
        self._add_register(MIIRegister(23, 1))
        self._add_register(MIIRegister(23, 2))

        self._add_register(MIIRegister(23, 7))
        self._add_register(MIIRegister(23, 8))
        self._add_register(MIIRegister(23, 9))
        if not self._nano:
            self._add_register(MIIRegister(23, 11))
            self._add_register(MIIRegister(23, 12))

        self._add_register(MIIRegister(23, 13))
        self._add_register(MIIRegister(23, 14))

        self._add_register(MIIRegister(23, 19))

        for i in range(25):
            self._add_register(MIIRegister(24, i))

    def _init_fields(self) -> None:
        # Example values of the VLAN-related registries
        # [23, 0, 0, 0],  # [-, VLAN_TABLE_CLR=128|UNVID_MODE=32]  # !UNVID_MODE=VLAN mode->enabled
        # [23, 1, 255, 0],  # [TAG_VLAN_EN=0, VLAN_CLS=0]  # VLAN_CLS=Force VLAN ID
        # [23, 2, 255, 0b00000100],  # [VLAN_INGRESS_FILTER=FF, 0b000, RSVD_VID=0b001, ACCEPTABLE_FRM_TYPE=0b00]
        #                               VLAN_INGRESS_FILTER=VLAN mode->strict, ACCEPTABLE_FRM_TYPE=VLAN receive
        # [23, 8, 2, 0],  # VLAN_INFO_1=1  # Default VLAN ID
        # [23, 12, 2, 0],  # VLAN_INFO_4=1  # Default VLAN ID
        # [23, 13, 0b00000000, 0],  # [ADD_TAG=0, -]  # VLAN Header->add if missing
        # [23, 14, 0b00000000, 0],  # [REMOVE_TAG=0, -]  # VLAN Header->always strip
        # [24, 0, 0b00000011, 0],  # VLAN_VALID=0
        # [24, 1, 2, 0],  # VID_0=1
        # [24, 2, 1, 0],  # VID_1=2
        # [24, 17, 0b10001000, 255],  # [VLAN_MEMBER_0=FF, VLAN_MEMBER_1=FF]

        Addr = MIIRegisterAddress  # noqa: N806

        self._add_field(BitField(self._registers[Addr(23, 0)], 13, False, 'UNVID_MODE'))
        self._add_field(BitField(self._registers[Addr(23, 0)], 15, False, 'VLAN_TABLE_CLR'))

        self._add_field(self._create_port_list_field(self._registers[Addr(23, 1)], 1, False, 'VLAN_CLS'))
        self._add_field(self._create_port_list_field(self._registers[Addr(23, 1)], 0, False, "TAG_VLAN_EN"))

        self._add_field(BitField(self._registers[Addr(23, 2)], 13, False, 'VLAN_DROP_CFI'))
        self._add_field(BitField(self._registers[Addr(23, 2)], 12, False, 'RSVD_VID_2'))
        self._add_field(BitField(self._registers[Addr(23, 2)], 11, False, 'RSVD_VID_1'))
        self._add_field(BitField(self._registers[Addr(23, 2)], 10, True, 'RSVD_VID_0'))
        self._add_field(BitsField(self._registers[Addr(23, 2)], 8, 2, 0, 'ACCEPTABLE_FRM_TYPE'))
        self._add_field(self._create_port_list_field(self._registers[Addr(23, 2)], 0, True, "VLAN_INGRESS_FILTER"))

        self._add_field(ShortField(self._registers[Addr(23, 7)], 0, 1, 'VLAN_INFO_0'))
        self._add_field(ShortField(self._registers[Addr(23, 8)], 0, 1, 'VLAN_INFO_1'))
        self._add_field(ShortField(self._registers[Addr(23, 9)], 0, 1, 'VLAN_INFO_2'))
        if not self._nano:
            self._add_field(ShortField(self._registers[Addr(23, 11)], 0, 1, 'VLAN_INFO_3'))
            self._add_field(ShortField(self._registers[Addr(23, 12)], 0, 1, 'VLAN_INFO_4'))

        self._add_field(self._create_port_list_field(self._registers[Addr(23, 13)], 0, False, "ADD_TAG"))
        self._add_field(self._create_port_list_field(self._registers[Addr(23, 14)], 0, False, "REMOVE_TAG"))

        self._add_field(BitField(self._registers[Addr(23, 19)], 2, False, 'LEAKY_VLAN_2'))
        self._add_field(BitField(self._registers[Addr(23, 19)], 1, False, 'LEAKY_VLAN_1'))
        self._add_field(BitField(self._registers[Addr(23, 19)], 0, False, 'LEAKY_VLAN_0'))

        self._add_field(BitsField(self._registers[Addr(24, 0)], 0, 16, 0, 'VLAN_VALID'))

        for i in range(16):
            self._add_field(BitsField(self._registers[Addr(24, i + 1)], 0, 12, i + 1, 'VID_{:1X}'.format(i)))

        for i in range(16):
            self._add_field(self._create_port_list_field(self._registers[Addr(24, 17 + (i // 2))], i % 2, True,
                                                         "VLAN_MEMBER_{:1X}".format(i)))

    class IP175GPortListField(PortListField):
        def __init__(self, register: MIIRegister, index: int, ports: List[Port], ports_default: bool, name: str) \
                -> None:
            super().__init__(register, ports, ports_default, name)
            self._base_field = ByteField(register, index, 255 if ports_default else 0, name)
            self._ports = ports if ports_default else list()

        def _add_port(self, port: Port, touch: bool = True) -> None:
            value = self._base_field.get_value()
            value |= 1 << port.id
            self._base_field.set_value(value, touch)

        def _remove_port(self, port: Port, touch: bool = True) -> None:
            value = self._base_field.get_value()
            value &= ~(1 << port.id)
            self._base_field.set_value(value, touch)

        def _clear(self, touch: bool = True) -> None:
            self._base_field.set_value(0, touch)

    def _create_port_list_field(self, register: MIIRegister, index: int, ports_default: bool, name: str) \
            -> PortListField:
        return IP175G.IP175GPortListField(register, index, self._ports, ports_default, name)

    def register_to_command(self, register: MIIRegister, leave_out_default: bool = True) -> Optional[List[int]]:
        """
        Convert the given register into a "command" for botblox firmware.
        :param register: The register to convert.
        :param leave_out_default: If true, returns None in case the register has its default value.
        :return: The firmware "command".
        """
        if leave_out_default and register.is_default():
            return None
        return [register.address.phy, register.address.mii] + register.as_bytes()

    def get_commands(self, leave_out_default: bool = True, only_touched: bool = False) -> List[List[int]]:
        """
        Create list of commands to be sent to the BotBlox firmware.

        Explicitly checks if VLANs have been configured and sets the VLAN_VALID register accordingly.
        For each configured VLAN, one bit is set in the VLAN_VALID register, starting from the LSB.
        For example:
            - 1 VLAN: VLAN_VALID = 1 (binary 1)
            - 2 VLANs: VLAN_VALID = 3 (binary 11)
            - 3 VLANs: VLAN_VALID = 7 (binary 111)

        :param leave_out_default: If True, registers with default values are omitted from commands
        :param only_touched: If True, only registers that have been modified are included
        :return: List of command lists to be sent to the firmware
        """
        configured_vlans = 0
        for i in range(16):
            vid_field_name = 'VID_{:1X}'.format(i)
            if vid_field_name in self.fields and self.fields[vid_field_name].is_touched():
                configured_vlans += 1
        
        if configured_vlans > 0 and 'VLAN_VALID' in self.fields:
            vlan_valid_value = (1 << configured_vlans) - 1
            self.fields['VLAN_VALID'].set_value(vlan_valid_value)

        result = list()
        for r in self._registers.values():
            cmd = self.register_to_command(r, leave_out_default)
            if cmd is not None and (not only_touched or r.is_touched()):
                result.append(cmd)
        result.sort()
        return result
