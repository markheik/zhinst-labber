from enum import Enum
from zhinst.labber.generator import function_section


def func_no_args():
    return 12


class EnumInp(Enum):
    foo = 1
    bar = "BAR123"


def func_args(enum: EnumInp, foobar: str, bar=1, foo="asd", *args, **kwargs) -> int:
    """This is a test function.

    It has things

    Args:
        enum: An enumerator.
        foobar: Foop
            Foop is a here
        bar: Barz
        foo: Does this.

    Returns:
        Return value.
    Thing here.
    """
    return 12


def test_function_to_group_func_no_args():
    r = function_section.function_to_group(func_no_args, "t")
    assert r == [
        {
            "datatype": "BUTTON",
            "group": "T - FUNC_NO_ARGS",
            "label": "EXECUTEFUNC",
            "section": "T",
            "tooltip": "<html><body><p></p></body></html>",
        },
    ]


def test_function_to_group_func_args():
    r = function_section.function_to_group(func_args, "t")
    assert r == [
        {
            "cmd_def_1": "1",
            "cmd_def_2": "BAR123",
            "combo_def_1": "foo",
            "combo_def_2": "bar",
            "datatype": "COMBO",
            "group": "T - FUNC_ARGS",
            "label": "ENUM",
            "permission": "WRITE",
            "section": "T",
            "tooltip": "<html><body><p>An enumerator.</p><p><ul><li>foo: 1</li><li>bar: "
            "BAR123</li></ul></p></body></html>",
        },
        {
            "datatype": "STRING",
            "group": "T - FUNC_ARGS",
            "label": "FOOBAR",
            "permission": "WRITE",
            "section": "T",
            "tooltip": "<html><body><p>Foop Foop is a here</p></body></html>",
        },
        {
            "datatype": "DOUBLE",
            "def_value": "1",
            "group": "T - FUNC_ARGS",
            "label": "BAR",
            "permission": "WRITE",
            "section": "T",
            "tooltip": "<html><body><p>Barz</p></body></html>",
        },
        {
            "datatype": "STRING",
            "def_value": "asd",
            "group": "T - FUNC_ARGS",
            "label": "FOO",
            "permission": "WRITE",
            "section": "T",
            "tooltip": "<html><body><p>Does this.</p></body></html>",
        },
        {
            "datatype": "BUTTON",
            "group": "T - FUNC_ARGS",
            "label": "EXECUTEFUNC",
            "section": "T",
            "tooltip": "<html><body><p>This is a test function.</p></body></html>",
        },
    ]


class PropertyModule:
    def __init__(self) -> None:
        pass

    def __iter__(self):
        ...


class BaseClass:
    def __init__(self):
        ...
        
    def activate(self, bar: int):
        ...
        
    def awg(self) -> PropertyModule:
        return PropertyModule()
    