import inspect
from docstring_parser import parse
import typing as t

from zhinst.toolkit.nodetree import Node
from .helpers import labber_delimiter, to_labber_format, tooltip
from .replaces_nodes import REPLACED_FUNCTIONS


def node_indexes(nodes: t.Dict[Node, dict], target: t.List[str]) -> t.List[str]:
    l_target = list((map(lambda x: x.lower(), target)))
    chs = []
    for k, v in nodes.items():
        path = v['Node'].lower().split('/')
        if all(x in path for x in l_target):
            idx_ = path.index(l_target[-1].lower())
            if idx_ < len(path) - 1:
                if path[idx_ + 1].isnumeric():
                    if path[idx_+1] not in chs:
                        chs.append(path[idx_+1])
    return chs


class FunctionParser:
    def __init__(self, nodes: t.Dict, ignores: t.List[str]):
        self.nodes = nodes
        self.ignores = ignores
        self._functions = []
        self.root = 'DEVICE'

    def get_functions(self, obj: object) -> t.List[t.Dict[str, str]]:
        self._function_generator(obj, 'DEVICE')
        return self._functions

    def _function_generator(self, obj, parent: str) -> None:
        if obj in self.ignores:
            return
        for name, attr in vars(obj).items():
            if attr in self.ignores:
                continue
            if name.startswith('_'):
                continue
            if isinstance(attr, property):
                th = t.get_type_hints(attr.fget)
                cls_ = th["return"]
                if "typing.Union" in str(cls_) or "typing.Sequence" in str(cls_):
                    for k in node_indexes(self.nodes, [name]):
                        self.root = labber_delimiter(name, k)
                        self._function_generator(cls_.__args__[0], self.root)
                elif inspect.isclass(cls_):
                    if issubclass(cls_, Node):
                        self._function_generator(cls_, labber_delimiter(self.root, name))
                    else:
                        continue
            else:
                d = {
                    'section': self.root,
                    'title': labber_delimiter(parent, name),
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
    return_type = signature.return_annotation

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
        item['section'] = section.upper()
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
        try:
            s = REPLACED_FUNCTIONS[obj][k]
            item.update(s)
        except KeyError:
            ...
        items.append(item)

    if return_type != inspect._empty and return_type is not None:
        permission = 'READ'
        if isinstance(return_type, int):
            dt = 'DOUBLE'
        if isinstance(return_type, bool):
            dt = 'BOOLEAN'
        if isinstance(return_type, float):
            dt = 'DOUBLE'
        if isinstance(return_type, str):
            dt = 'STRING'
        else:
            dt = 'PATH'
    else:
        dt = 'BOOLEAN'
        permission = 'WRITE'

    d = {
        'label': 'EXECUTEFUNC', 
        'datatype': dt, 
        'permission': permission,
        'group': labber_delimiter(section.upper(), group.upper()),
        'section': section.upper() if section else 'DEVICE',
        'tooltip': tooltip(docstring.short_description),
    }
    if permission == 'READ' and dt == 'PATH':
        d['get_cmd'] = 'csv'
    else:
        d['set_cmd'] = labber_delimiter(section.upper(), group.upper())

    items.append(d)
    return items


def functions_to_config(class_: object, nodes: t.Dict[Node, t.Dict], ignores: t.List[str]) -> t.Dict:
    o = FunctionParser(nodes=nodes, ignores=ignores)
    fs = {}
    for item in o.get_functions(class_):
        for func in function_to_group(item['obj'], item['section']):
            section = labber_delimiter(item['title'], func['label'])
            func['group'] = item['title']
            fs[section] = func
    return fs
