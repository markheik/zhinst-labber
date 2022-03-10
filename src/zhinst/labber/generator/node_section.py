import typing as t

from . import helpers

class NodeSection:
    def __init__(self, node: t.Dict):
        self.node = node
        self.node.setdefault("Options", {})
        self._node_path = helpers.delete_device_from_node_path(node["Node"].upper())
        self._node_path_no_prefix = self._node_path.removeprefix('/')
        self._properties = self.node["Properties"].lower()

    @property
    def filtered_node_path(self):
        return self._node_path

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
        parsed = self._node_path_no_prefix.upper().split("/")
        for idx, x in enumerate(parsed, 1):
            if idx == 3:
                break
            if x.isnumeric():
                return helpers.labber_delimiter(*parsed[0:idx])
        return parsed[0]

    @property
    def group(self) -> str:
        node_path = self._node_path_no_prefix
        path = [x for x in node_path.split("/") if not x.isnumeric()]
        if len(path) > 1:
            return helpers.labber_delimiter(*path[:-1])
        return helpers.labber_delimiter(*path)

    @property
    def label(self) -> str:
        node_path = self._node_path_no_prefix
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
        node_path = self._node_path_no_prefix.upper()
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
            return self._node_path_no_prefix

    @property
    def get_cmd(self) -> t.Optional[str]:
        if "read" in self._properties:
            return self._node_path_no_prefix

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

        # # Overwrite Sections
        # r = REPLACED_NODES.get(replace_node_ch_n(self._node_path), {})
        # d.update(r)
        # for k, v in NODE_SECTIONS['SHFQA'].items():
        #     r = fnmatch.filter([self._node_path.upper()], f'{k}*')
        #     if r:
        #         d['section'] = v
        #         break
        # # Overwrite groups
        # for k, v in NODE_GROUPS['SHFQA'].items():
        #     r = fnmatch.filter([self._node_path.upper()], f'{k}*')
        #     if r:
        #         d['group'] = v
        #         break

        return {self.label: d}
