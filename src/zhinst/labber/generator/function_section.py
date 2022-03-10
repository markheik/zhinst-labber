from copy import deepcopy
import inspect
from docstring_parser import parse
import typing as t

from zhinst.toolkit.nodetree import Node
from .helpers import labber_delimiter, to_labber_format, tooltip, to_labber_combo_def
from .conf import REPLACED_FUNCTIONS


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
                d = {
                    'section': self.root,
                    'title': labber_delimiter(parent, name),
                    'name': name,
                    'obj': attr
                }
                self._functions.append(d)

def function_to_group(obj, section: str, title: str) -> t.Dict:
    """Native Python function."""
    items = {}
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
        item['group'] = title
        item['section'] = section.upper()
        if v.default != inspect._empty:
            if 'enum' in str(type(v.default)):
                item['def_value'] = str(v.default.name)
            else:
                item['def_value'] = str(v.default)
        item['permission'] = 'WRITE'
        if item['datatype'] == 'PATH':
            item['set_cmd'] = '*.csv'
        if item['datatype'] == 'COMBO':
            item.update(to_labber_combo_def(v.annotation))

        for param in docstring.params:
            if k == param.arg_name:
                enum = []
                if item['datatype'] == 'COMBO':
                    if v.annotation != inspect._empty:
                        enum = [f'{k.name}: {k.value}' for k in v.annotation]
                    else:
                        enum = [f'{k.name}: {k.value}' for k in type(v.default)]

                item['tooltip'] = tooltip(param.description, enum=enum)
        items[labber_delimiter(title, item['label'])] = item

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
            dt = 'STRING'
    else:
        dt = 'BOOLEAN'
        permission = 'WRITE'

    d = {
        'label': 'Executefunc', 
        'datatype': dt,
        'permission': permission,
        'group': title,
        'section': section.upper() if section else 'DEVICE',
        'tooltip': tooltip(docstring.short_description),
    }
    if permission == 'WRITE' and dt == 'PATH':
        d['set_cmd'] = '*.csv'
    else:
        d['get_cmd'] = labber_delimiter(section.upper(), group.upper())
    items[labber_delimiter(title, d['label'])] = d
    

    item_keys = [x.lower() for x in items.keys()]
    try:
        for k, v in REPLACED_FUNCTIONS[obj].items():
            _v = deepcopy(v)
            title_ = labber_delimiter(title, v.get('label', k))
            if title_.lower() in item_keys:
                if not _v:
                    items.pop(title_, None)
                else:
                    items[title_].update(_v)
            else:
                _v['group'] = title
                _v['section'] = v.get('section', section)
                items[title_] = _v
    except KeyError:
        ...
    return items


def functions_to_config(class_: object, nodes: t.Dict[Node, t.Dict], ignores: t.List[str]) -> t.Dict:
    o = FunctionParser(nodes=nodes, ignores=ignores)
    fs = {}
    for item in o.get_functions(class_):
        fs.update(function_to_group(item['obj'], item['section'], item['title']))
    return fs
