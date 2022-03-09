import typing as t
import re

from zhinst.toolkit.nodetree import Node
from zhinst.labber.generator import LABBER_DELIMITER_VALUE


def enum_description(value: str) -> t.Tuple[str, str]:
    v = value.split(': ')
    if len(v) > 1:
        v2 = v[0].split(',')
        return v2[0].strip('"'), v[-1]
    return "", v[0]

def to_labber_format(obj) -> str:
    TYPE_MAP = {
        str: 'STRING',
        int: 'DOUBLE',
        bool: 'BOOLEAN',
        Node: 'STRING',
        float: 'DOUBLE',
        dict: 'PATH'
    }
    if 'enum' in str(obj):
        return 'COMBO'
    str_obj = str(obj)
    if 'typing' in str_obj:
        if 'dict' in str_obj.lower():
            return 'PATH'
        if 'list' in str_obj.lower():
            return 'PATH'
    try:
        return TYPE_MAP[obj]
    except KeyError:
        return 'NONE'

def _replace_characters(s: str) -> str:
    if not s:
        return ''
    return s.replace('\n', ' ').replace('\r', '').replace('"', '`').replace("'", '`').replace(";", ':').replace("%", " percent")

def labber_delimiter(*args: str) -> str:
    return LABBER_DELIMITER_VALUE.join(args).upper()

def _to_html_list(x: t.List[str]) -> str:
    html_list = "<ul>"
    for item in x:
        item_cleaned = _replace_characters(item)
        html_list += f"<li>{item_cleaned}</li>"
    html_list += "</ul>"
    return html_list

def tooltip(desc, node = None, enum = None) -> str:
    desc_cleaned = _replace_characters(desc)
    desc = f'<p>{desc_cleaned}</p>'
    enum = f'<p>{_to_html_list(enum)}</p>' if enum else ''
    node_path = f'<p><b>{node.strip()}</b></p>' if node else ''
    return '<html><body>' + desc + enum + node_path + '</body></html>'

def delete_device_from_node_path(path: str) -> str:
    return re.sub(r"/DEV(\d+)", "", path)[0:]
