import typing as t
import re
from enum import Enum, IntEnum
import fnmatch
from zhinst.toolkit.nodetree import Node


def remove_leading_trailing_slashes(string: str) -> str:
    if len(string.split("/")) <= 1:
        return string.replace("/", "")
    str_l = list(string)
    if str_l[0] == "/":
        str_l[0] = ""
    if str_l[-1] == "/":
        str_l[-1] = ""
    return "".join(str_l)


def enum_description(value: str) -> t.Tuple[str, str]:
    v = value.split(": ")
    if len(v) > 1:
        v2 = v[0].split(",")
        return v2[0].strip('"'), v[-1]
    return "", v[0]


def to_labber_format(obj) -> str:
    TYPE_MAP = {
        str: "STRING",
        int: "DOUBLE",
        bool: "BOOLEAN",
        Node: "STRING",
        float: "DOUBLE",
        dict: "PATH",
    }
    if "enum" in str(obj):
        return "COMBO"
    str_obj = str(obj)
    if "typing" in str_obj:
        if "dict" in str_obj.lower():
            return "PATH"
        if "list" in str_obj.lower():
            return "PATH"
    try:
        return TYPE_MAP[obj]
    except KeyError:
        return "STRING"


def _replace_characters(s: str) -> str:
    s_ = s
    if not s:
        return ""
    chars = [
        ("\n", " "),
        ("\r", ""),
        ('"', "`"),
        ("'", "`"),
        (";", ":"),
        ("%", " percent"),
    ]
    for c in chars:
        s_ = s_.replace(c[0], c[1])
    return s_


def _to_html_list(x: t.List[str]) -> str:
    html_list = "<ul>"
    for item in x:
        item_cleaned = _replace_characters(item)
        html_list += f"<li>{item_cleaned}</li>"
    html_list += "</ul>"
    return html_list


def tooltip(
    desc: str, node: t.Optional[str] = None, enum: t.Optional[t.List[str]] = None
) -> str:
    """Convert tooltip arguments to HTML.

    Args:
        desc: Paragraph
        node: Bolded text part.
        enum: String to be converted to an HTML list.
    """
    if desc.startswith("<html>"):
        return desc
    desc_cleaned = _replace_characters(desc)
    desc = f"<p>{desc_cleaned}</p>"
    enum = f"<p>{_to_html_list(enum)}</p>" if enum else ""
    node_path = f"<p><b>{node.strip()}</b></p>" if node else ""
    return "<html><body>" + desc + enum + node_path + "</body></html>"


def delete_device_from_node_path(path: str) -> str:
    return re.sub(r"/DEV(\d+)", "", path.upper())[0:]


def to_labber_combo_def(
    iterable_: t.Union[t.List[str], t.Dict[str, t.Union[str, int, float]], t.Any]
):
    enums = {}
    if isinstance(iterable_, list):
        for idx, enum in enumerate(iterable_, 1):
            enums[f"cmd_def_{idx}"] = str(enum)
            enums[f"combo_def_{idx}"] = str(enum)
    elif isinstance(iterable_, dict):
        for idx, (k, v) in enumerate(iterable_.items(), 1):
            enums[f"cmd_def_{idx}"] = str(k)
            enums[f"combo_def_{idx}"] = str(v)
    elif issubclass(iterable_, (Enum, IntEnum)):
        for idx, enum in enumerate(iterable_, 1):
            enums[f"cmd_def_{idx}"] = str(enum.value)
            enums[f"combo_def_{idx}"] = str(enum.name)
    return enums


def match_in_dict_keys(target: str, data: dict) -> t.Tuple[str, t.Any]:
    """Find matches for target in data."""
    for k, v in data.items():
        k_ = remove_leading_trailing_slashes(k)
        target = remove_leading_trailing_slashes(target)
        r = fnmatch.filter([target.lower()], f"{k_.lower()}*")
        if r:
            return k, v
    return "", {}


def match_in_list(target: str, data: list) -> t.List[str]:
    for item in data:
        k_ = remove_leading_trailing_slashes(item)
        target = remove_leading_trailing_slashes(target)
        r = fnmatch.filter([target.lower()], f"{k_.lower()}*")
        if r:
            return item
    return []


def find_nth_occurence(s: str, target: str, n: int) -> int:
    """Find nth occurrence of the target in a string"""
    if s.count(target) < n + 1:
        return -1
    return s.find(target, s.find(target) + n)
