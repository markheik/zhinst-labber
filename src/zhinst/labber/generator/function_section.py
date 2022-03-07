import inspect
from docstring_parser import parse
import typing as t

from zhinst.toolkit.nodetree import Node
from .helpers import labber_delimiter, to_labber_format, tooltip


def node_indexes(nodes: t.Dict[Node, dict], target: t.List[str]) -> t.List[str]:
    chs = []
    for k, v in nodes.items():
        path = v['Node'].lower().split('/')
        if all(x in path for x in target):
            idx_ = path.index(target[-1])
            if path[idx_ + 1].isnumeric():
                if path[idx_+1] not in chs:
                    chs.append(path[idx_+1])
    return chs


def nodes_to_dict(node: Node) -> t.Dict:
    return {k[0]: k[1] for k in node}

class FunctionParser:
    def __init__(self, nodes: t.Dict, ignores: t.List[str]):
        self.nodes = nodes
        self.ignores = ignores
        self.path = ''
        self.root_path = ''
        self._functions = []

    def get_functions(self, obj: object) -> t.List[t.Dict[str, str]]:
        self._function_generator(obj)
        return self._functions

    def _function_generator(self, obj):
        for name, attr in vars(obj).items():
            if name in self.ignores:
                continue
            if name.startswith('_'):
                continue
            if isinstance(attr, property):
                th = t.get_type_hints(attr.fget)
                if "typing.Union" in str(th["return"]) or "typing.Sequence" in str(th["return"]):
                    self.path = ''
                    self.path = labber_delimiter(self.path, name) if self.path else name
                    for k in node_indexes(self.nodes, [name]):
                        self.path = labber_delimiter(self.path, k)
                        self.root_path = self.path
                        self._function_generator(th['return'].__args__[0])
                elif inspect.isclass(th["return"]):
                    if issubclass(th["return"], Node):
                        self.root_path = self.path
                        self.path = labber_delimiter(self.path, name) if self.path else name
                        self._function_generator(th['return'])
                        self.path = self.root_path
                    else:
                        continue
            else:
                d = {
                    'section': self.root_path if self.root_path else 'DEVICE',
                    'section_name': self.path if self.path else 'DEVICE',
                    'name': name,
                    'obj': attr
                }
                self._functions.append(d)


def function_to_group(obj, section: str) -> t.List[t.Dict]:
    """Native Python function."""
    items = []
    group = obj.__name__
    signature = inspect.signature(obj)
    docstring = parse(obj.__doc__)

    for k, v in signature.parameters.items():
        if k == ('self') or str(v).startswith('*'):
            continue
        item = {}
        item['label'] = k.upper()
        if v.annotation != inspect._empty:
            item['datatype'] = to_labber_format(v.annotation)
        else:
            item['datatype'] = to_labber_format(type(v.default))
        item['group'] = labber_delimiter(section.upper(), group.upper())
        item['section'] = section.upper() if section else 'DEVICE'
        if v.default != inspect._empty:
            if 'enum' in str(type(v.default)):
                item['def_value'] = str(v.default.name)
            else:
                item['def_value'] = str(v.default)
        item['permission'] = 'WRITE'
        if item['datatype'] == 'COMBO':
            for idx, enum in enumerate(v.annotation, 1):
                item[f'cmd_def_{idx}'] = str(enum.value)
                item[f'combo_def_{idx}'] = str(enum.name)

        for param in docstring.params:
            if k == param.arg_name:
                enum = []
                if item['datatype'] == 'COMBO':
                    if v.annotation != inspect._empty:
                        enum = [f'{k.name}: {k.value}' for k in v.annotation]
                    else:
                        enum = [f'{k.name}: {k.value}' for k in type(v.default)]

                item['tooltip'] = tooltip(param.description, enum=enum)
        items.append(item)
    items.append(
        {
            'label': 'EXECUTEFUNC', 
            'datatype': 'BUTTON', 
            'group': labber_delimiter(section.upper(), group.upper()),
            'section': section.upper() if section else 'DEVICE',
            'tooltip': tooltip(docstring.short_description),
        }
    )
    return items


def functions_to_config(class_: object, nodes: t.Dict[Node, t.Dict], ignores: t.List[str]) -> t.List:
    o = FunctionParser(nodes=nodes, ignores=ignores)
    sections = []
    for item in o.get_functions(class_):
        fs = {}
        for func in function_to_group(item['obj'], item['section']):
            section = labber_delimiter(item['section_name'], item['name'], func['label'])
            func['group'] = labber_delimiter(item['section_name'], item['name'])
            fs[section] = func
        sections.append(fs)
    return sections
