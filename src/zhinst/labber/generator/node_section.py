import typing as t
import re
from functools import wraps
from . import helpers


class NodeSection:
    def __init__(self, node: dict):
        self.node = node
        self.node.setdefault('Options', {})
        self._node_path = node["Node"].upper()
        self._properties = self.node["Properties"].lower()
        self.replaced = {}

    def replacer(key):
        def replacer(func):
            @wraps(func)
            def wraps_(self, *args, **kwargs):
                try:
                    return self.replaced[self._delete_root_node(self._node_path)][key]
                except KeyError:
                    return func(self, *args, **kwargs)
            return wraps_
        return replacer

    def permission(self) -> str:
        if "read" in self._properties and "write" in self._properties:
            return "BOTH"
        if "read" in self._properties:
            return "READ"
        if "write" in self._properties:
            return "WRITE"
        return "NONE"

    def show_in_measurement_dlg(self) -> t.Optional[str]:
        if self.node["Type"] in ["VECTOR", "COMPLEX", "VECTOR_COMPLEX"]:
            return "True"

    def section(self) -> str:
        parsed = self._delete_root_node(self._node_path.upper()).split("/")
        for idx, x in enumerate(parsed, 1):
            if idx == 3:
                break
            if x.isnumeric():
                return helpers.labber_delimiter(*parsed[0:idx])
        return parsed[0]

    def group(self) -> str:
        node_path = self._delete_root_node(self._node_path)
        path = [x for x in node_path.split("/") if not x.isnumeric()]
        if len(path) > 1:
            return helpers.labber_delimiter(*path[:-1])
        return helpers.labber_delimiter(*path)

    def label(self) -> str:
        node_path = self._delete_root_node(self._node_path)
        path = node_path.split("/")
        return helpers.labber_delimiter(*path)

    def combo_def(self) -> t.List[dict]:
        if "enumerated" in self.node["Type"].lower():
            if "READ" == self.permission():
                return []
        opt = self.node['Options']
        combos = []
        for idx, (k, v) in enumerate(opt.items(), 1):
            value, _ = helpers.enum_description(v)
            res = {
                f"cmd_def_{idx}": value if value else str(k),
                f"combo_def_{idx}": value if value else str(k),
            }
            combos.append(res)
        return combos

    def tooltip(self) -> str:
        node_path = self._delete_root_node(self._node_path.upper()).upper()
        items = []
        for k, v in self.node["Options"].items():
            value, desc = helpers.enum_description(v)
            items.append(f"{value if value else k}: {desc}")
        return helpers.tooltip(self.node["Description"], enum=items, node=node_path)

    def unit(self) -> t.Optional[str]:
        if self.node["Unit"] == "None":
            return None
        unit = self.node["Unit"].replace("%", " percent").replace("'", "")
        # Remove degree signs etc.
        return unit.encode("ascii", "ignore").decode()

    @replacer("datatype")
    def datatype(self) -> t.Optional[str]:
        unit = self.node["Type"]
        if "enumerated" in unit.lower():
            if not "READ" == self.permission():
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

    def _delete_root_node(self, path: str) -> str:
        return re.sub(r"/DEV(\d+)", "", path)[1:]

    def set_cmd(self) -> t.Optional[str]:
        if "read" in self._properties:
            return self._delete_root_node(self._node_path)

    def get_cmd(self) -> t.Optional[str]:
        if "write" in self._properties:
            return self._delete_root_node(self._node_path)

    def to_config(self, config):
        sec_namex = self.label()
        config.add_section(sec_namex)
        config.set(sec_namex, "section", self.section())
        config.set(sec_namex, "group", self.group())
        config.set(sec_namex, "label", self.label())
        config.set(sec_namex, "datatype", self.datatype()) if self.datatype() else ...
        config.set(sec_namex, "unit", self.unit()) if self.unit() else ...
        config.set(sec_namex, "tooltip", self.tooltip())

        for item in self.combo_def():
            for k, v in item.items():
                config.set(sec_namex, k, v)

        config.set(sec_namex, "permission", self.permission()) if self.permission() else ...
        config.set(sec_namex, "set_cmd", self.set_cmd()) if self.set_cmd() else ...
        config.set(sec_namex, "get_cmd", self.get_cmd()) if self.get_cmd() else ...
        config.set(sec_namex, "show_in_measurement_dlg", self.show_in_measurement_dlg()) if self.show_in_measurement_dlg() else ...