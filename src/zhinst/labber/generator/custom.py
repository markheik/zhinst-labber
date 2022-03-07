import typing as t
import configparser
from .helpers import tooltip


class CustomLabel:
    def __init__(self, name: str, section: str, group: str):
        self._name = name
        self._section = section
        self._group = group
        self._items = {}
        self._combos = []
        self._tt_desc = ''
        self._tt_node = ''
        self._tt_enums: t.List[str] = []

    def __setitem__(self, key, value):
        self._items[key] = value

    def __getitem__(self, key):
        return self._items[key]

    def add_enum(self, cmd_def: str, combo_def: str, desc: str):
        self._combos.append((cmd_def, combo_def, desc))

    def tooltip(self, desc: str, node: t.Optional[str] = None):
        self._tt_desc = desc
        self._tt_node = node

    def items(self):
        return self._items

    def combos(self) -> t.Dict:
        d = {}
        for idx,c in enumerate(self._combos, 1):
            d[f'cmd_def{idx}'] = c[0]
            d[f'combo_def{idx}'] = c[1]
            self._tt_enums.append(f'{c[1]}: {c[2]}')
        return d

    def to_config(self, config: configparser.ConfigParser):
        config.add_section(self._name)
        config.set(self._name, 'group', self._group)
        config.set(self._name, 'section', self._section)
        for k, v in self._items.items():
            config.set(self._name, k, v)

        for idx,c in enumerate(self._combos, 1):
            config.set(self._name, f'cmd_def{idx}', c[0])
            config.set(self._name, f'combo_def{idx}', c[1])
            self._tt_enums.append(f'{c[1]}: {c[2]}')
        config.set(self._name, 'tooltip', tooltip(self._tt_desc, self._tt_node, self._tt_enums))