import configparser
import typing as t
import re
from functools import wraps
from . import helpers
from .replaces_nodes import REPLACED_NODES


def replace_node_ch_n(node: str) -> str:
    replaced = []
    for c in node.upper().split('/'):
        if c.isnumeric():
            replaced.append('N')
        else:
            replaced.append(c)
    return '/'.join(replaced)

class NodeSection:
    def __init__(self, node: t.Dict):
        self.node = node
        self.node.setdefault("Options", {})
        self._node_path = self._delete_root_node(node["Node"].upper())
        self._properties = self.node["Properties"].lower()

    def _delete_root_node(self, path: str) -> str:
        return re.sub(r"/DEV(\d+)", "", path)[1:]

    # def replacer(key):
    #     def replacer(func):
    #         @wraps(func)
    #         def wraps_(self, *args, **kwargs):
    #             try:
    #                 return self.replaced[self._node_path][key]
    #             except KeyError:
    #                 return func(self, *args, **kwargs)
    #         return wraps_
    #     return replacer

    @property
    def permission(self) -> str:
        if "read" in self._properties and "write" in self._properties:
            return "BOTH"
        if "read" in self._properties:
            return "READ"
        if "write" in self._properties:
            return "WRITE"
        return "NONE"

    @property
    def show_in_measurement_dlg(self) -> t.Optional[str]:
        if self.node["Type"] in ["VECTOR", "COMPLEX", "VECTOR_COMPLEX"]:
            return "True"

    @property
    def section(self) -> str:
        parsed = self._node_path.upper().split("/")
        for idx, x in enumerate(parsed, 1):
            if idx == 3:
                break
            if x.isnumeric():
                return helpers.labber_delimiter(*parsed[0:idx])
        return parsed[0]

    @property
    def group(self) -> str:
        node_path = self._node_path
        path = [x for x in node_path.split("/") if not x.isnumeric()]
        if len(path) > 1:
            return helpers.labber_delimiter(*path[:-1])
        return helpers.labber_delimiter(*path)

    @property
    def label(self) -> str:
        node_path = self._node_path
        path = node_path.split("/")
        return helpers.labber_delimiter(*path)

    @property
    def combo_def(self) -> t.List[dict]:
        if "enumerated" in self.node["Type"].lower():
            if "READ" == self.permission:
                return []
        opt = self.node["Options"]
        combos = []
        for idx, (k, v) in enumerate(opt.items(), 1):
            value, _ = helpers.enum_description(v)
            res = {
                f"cmd_def_{idx}": value if value else str(k),
                f"combo_def_{idx}": value if value else str(k),
            }
            combos.append(res)
        return combos

    @property
    def tooltip(self) -> str:
        node_path = self._node_path.upper().upper()
        items = []
        for k, v in self.node["Options"].items():
            value, desc = helpers.enum_description(v)
            items.append(f"{value if value else k}: {desc}")
        return helpers.tooltip(self.node["Description"], enum=items, node=node_path)

    @property
    def unit(self) -> t.Optional[str]:
        if self.node["Unit"] == "None":
            return None
        unit = self.node["Unit"].replace("%", " percent").replace("'", "")
        # Remove degree signs etc.
        return unit.encode("ascii", "ignore").decode()

    # @replacer("datatype")
    @property
    def datatype(self) -> t.Optional[str]:
        unit = self.node["Type"]
        if "enumerated" in unit.lower():
            if not "READ" == self.permission:
                return "COMBO"
        boolean_nodes = ["ENABLE", "SINGLE", "ON"]
        if self.node["Node"].split("/")[-1].upper() in boolean_nodes:
            return "BOOLEAN"
        if unit == "Double" or "integer" in unit.lower():
            return "DOUBLE"
        if unit == "Complex":
            return unit.upper()
        if unit == "ZIVectorData":
            return "VECTOR"
        if unit == "String":
            return "STRING"
        if unit == "ZIAdvisorWave":
            return "VECTOR"
        if unit == "Complex Double":
            return "COMPLEX"
        if unit == "ZIVectorData":
            return "VECTOR"
        if unit == "ZIDemodSample":
            return "VECTOR"
        if unit == "ZIDIOSample":
            return "VECTOR"

    @property
    def set_cmd(self) -> t.Optional[str]:
        if "write" in self._properties:
            return self._node_path

    @property
    def get_cmd(self) -> t.Optional[str]:
        if "read" in self._properties:
            return self._node_path

    def as_dict(self) -> dict:
        d = {}
        d['section'] = self.section
        d['group'] = self.group
        d['label'] = self.label
        if self.datatype:
            d['datatype'] = self.datatype
        if self.unit:
            d['unit'] = self.unit
        d['tooltip'] = self.tooltip
        for item in self.combo_def:
            for k, v in item.items():
                d[k] = v
        if self.permission:
            d['permission'] = self.permission
        if self.set_cmd:
            d['set_cmd'] = self.set_cmd
        if self.get_cmd:
            d['get_cmd'] = self.get_cmd
        if self.show_in_measurement_dlg:
            d['show_in_measurement_dlg'] = self.show_in_measurement_dlg

        path = '/' + self._node_path if not self._node_path.startswith('/') else self._node_path
        r = REPLACED_NODES.get(replace_node_ch_n(path), {})
        d.update(r)
        return d

    def to_config(self, config: configparser.ConfigParser) -> None:
        config.add_section(self.label)
        for k, v in self.as_dict().items():
            config.set(self.label, k, v)

        # config.add_section(sec_name)
        # config.set(sec_name, "section", self.section)
        # config.set(sec_name, "group", self.group)
        # config.set(sec_name, "label", self.label)
        # config.set(sec_name, "datatype", self.datatype) if self.datatype else ...
        # config.set(sec_name, "unit", self.unit) if self.unit else ...
        # config.set(sec_name, "tooltip", self.tooltip)

        # for item in self.combo_def:
        #     for k, v in item.items():
        #         config.set(sec_name, k, v)

        # config.set(
        #     sec_name, "permission", self.permission
        # ) if self.permission else ...
        # config.set(sec_name, "set_cmd", self.set_cmd) if self.set_cmd else ...
        # config.set(sec_name, "get_cmd", self.get_cmd) if self.get_cmd else ...
        # config.set(
        #     sec_name, "show_in_measurement_dlg", self.show_in_measurement_dlg
        # ) if self.show_in_measurement_dlg else ...
