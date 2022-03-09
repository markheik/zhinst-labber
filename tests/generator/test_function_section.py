from enum import Enum
from lib2to3.pytree import Base
import typing as t
import pytest

from zhinst.labber.generator import function_section
from zhinst.labber.generator.function_section import (
    FunctionParser,
    node_indexes,
    functions_to_config,
)
from zhinst.toolkit.nodetree import Node
from zhinst.toolkit.driver.nodes.generator import Generator as ZIGen


def test_function_to_group_func_replace():
    r = function_section.function_to_group(
        ZIGen.load_sequencer_program, "section", "title"
    )
    assert r == {
        "TITLE - EXECUTEFUNC": {
            "datatype": "BOOLEAN",
            "group": "SECTION - LOAD_SEQUENCER_PROGRAM",
            "label": "EXECUTEFUNC",
            "permission": "WRITE",
            "section": "SECTION",
            "set_cmd": "SECTION - LOAD_SEQUENCER_PROGRAM",
            "tooltip": "<html><body><p>Compiles and loads a "
            "sequencer program.</p></body></html>",
        },
        "TITLE - SEQUENCER_PROGRAM": {
            "datatype": "PATH",
            "group": "SECTION - LOAD_SEQUENCER_PROGRAM",
            "label": "SEQUENCER_PROGRAM",
            "permission": "WRITE",
            "section": "SECTION",
            "tooltip": "<html><body><p>Sequencer program to "
            "be uploaded</p></body></html>",
        },
        "TITLE - TIMEOUT": {
            "datatype": "DOUBLE",
            "def_value": "10",
            "group": "SECTION - LOAD_SEQUENCER_PROGRAM",
            "label": "TIMEOUT",
            "permission": "WRITE",
            "section": "SECTION",
            "tooltip": "<html><body><p>Maximum time to wait for the "
            "compilation on the device in seconds. "
            "(default = 10s)</p></body></html>",
        },
    }


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
    r = function_section.function_to_group(func_no_args, "section", "title")
    assert r == {
        "TITLE - EXECUTEFUNC": {
            "datatype": "BOOLEAN",
            "group": "SECTION - FUNC_NO_ARGS",
            "label": "EXECUTEFUNC",
            "permission": "WRITE",
            "section": "SECTION",
            "set_cmd": "SECTION - FUNC_NO_ARGS",
            "tooltip": "<html><body><p></p></body></html>",
        }
    }


def test_function_to_group_func_args():
    r = function_section.function_to_group(func_args, "section", "title")
    assert r == {
        "TITLE - BAR": {
            "datatype": "DOUBLE",
            "def_value": "1",
            "group": "SECTION - FUNC_ARGS",
            "label": "BAR",
            "permission": "WRITE",
            "section": "SECTION",
            "tooltip": "<html><body><p>Barz</p></body></html>",
        },
        "TITLE - ENUM": {
            "cmd_def_1": "1",
            "cmd_def_2": "BAR123",
            "combo_def_1": "foo",
            "combo_def_2": "bar",
            "datatype": "COMBO",
            "group": "SECTION - FUNC_ARGS",
            "label": "ENUM",
            "permission": "WRITE",
            "section": "SECTION",
            "tooltip": "<html><body><p>An enumerator.</p><p><ul><li>foo: "
            "1</li><li>bar: "
            "BAR123</li></ul></p></body></html>",
        },
        "TITLE - EXECUTEFUNC": {
            "datatype": "PATH",
            "get_cmd": "csv",
            "group": "SECTION - FUNC_ARGS",
            "label": "EXECUTEFUNC",
            "permission": "READ",
            "section": "SECTION",
            "tooltip": "<html><body><p>This is a test " "function.</p></body></html>",
        },
        "TITLE - FOO": {
            "datatype": "STRING",
            "def_value": "asd",
            "group": "SECTION - FUNC_ARGS",
            "label": "FOO",
            "permission": "WRITE",
            "section": "SECTION",
            "tooltip": "<html><body><p>Does this.</p></body></html>",
        },
        "TITLE - FOOBAR": {
            "datatype": "STRING",
            "group": "SECTION - FUNC_ARGS",
            "label": "FOOBAR",
            "permission": "WRITE",
            "section": "SECTION",
            "tooltip": "<html><body><p>Foop Foop is a " "here</p></body></html>",
        },
    }


def test_node_indexes():
    nodes = {
        "Node1": {"Node": "DEV123/AWG/0/foobar"},
        "Node2": {"Node": "DEV123/AWG/1/foobar"},
    }
    target = ["AWG"]
    r = node_indexes(nodes, target)
    assert r == ["0", "1"]

    nodes = {
        "Node1": {"Node": "DEV123/AWG/foobar"},
        "Node2": {"Node": "DEV123/AWG/foobar"},
    }
    target = ["awg"]
    r = node_indexes(nodes, target)
    assert r == []

    nodes = {
        "Node1": {"Node": "DEV123/AWG/foobar"},
        "Node2": {"Node": "DEV123/AWG/foobar"},
    }
    target = ["foobar"]
    r = node_indexes(nodes, target)
    assert r == []


class Generator(Node):
    def __init__(self):
        ...

    def gen_func(self):
        ...


class PropertyModule(Node):
    def __init__(self):
        pass

    def cool_function(self):
        ...

    @property
    def generator(self) -> Generator:
        ...


class PropertyModuleNo2(Node):
    def __init__(self):
        pass

    def cool_function2(self):
        ...


class BaseClass(Node):
    def __init__(self):
        ...

    def activate(self):
        ...

    def deactivate(self):
        ...

    @property
    def awg(self) -> t.Sequence[PropertyModule]:
        ...

    @property
    def chs(self) -> PropertyModuleNo2:
        ...


def test_function_parser():
    nodes = {
        "Node1": {"Node": "DEV123/AWG/0/PropertyModule"},
        "Node2": {"Node": "DEV123/AWG/1/PropertyModule"},
    }
    obj = FunctionParser(nodes, ignores=[])
    r = obj.get_functions(BaseClass)
    assert r == [
        {
            "name": "activate",
            "obj": BaseClass.activate,
            "section": "DEVICE",
            "title": "DEVICE - ACTIVATE",
        },
        {
            "name": "deactivate",
            "obj": BaseClass.deactivate,
            "section": "DEVICE",
            "title": "DEVICE - DEACTIVATE",
        },
        {
            "name": "cool_function",
            "obj": PropertyModule.cool_function,
            "section": "AWG - 0",
            "title": "AWG - 0 - COOL_FUNCTION",
        },
        {
            "name": "gen_func",
            "obj": Generator.gen_func,
            "section": "AWG - 0",
            "title": "AWG - 0 - GENERATOR - GEN_FUNC",
        },
        {
            "name": "cool_function",
            "obj": PropertyModule.cool_function,
            "section": "AWG - 1",
            "title": "AWG - 1 - COOL_FUNCTION",
        },
        {
            "name": "gen_func",
            "obj": Generator.gen_func,
            "section": "AWG - 1",
            "title": "AWG - 1 - GENERATOR - GEN_FUNC",
        },
        {
            "name": "cool_function2",
            "obj": PropertyModuleNo2.cool_function2,
            "section": "AWG - 1",
            "title": "AWG - 1 - CHS - COOL_FUNCTION2",
        },
    ]


def test_functions_to_config():
    nodes = {
        "Node1": {"Node": "DEV123/AWG/0/PropertyModule"},
        "Node2": {"Node": "DEV123/AWG/1/PropertyModule"},
    }
    ignores = [BaseClass.deactivate]
    r = functions_to_config(BaseClass, nodes=nodes, ignores=ignores)
    assert r == {
        "AWG - 0 - COOL_FUNCTION - EXECUTEFUNC": {
            "datatype": "BOOLEAN",
            "group": "AWG - 0 - COOL_FUNCTION",
            "label": "EXECUTEFUNC",
            "permission": "WRITE",
            "section": "AWG - 0",
            "set_cmd": "AWG - 0 - COOL_FUNCTION",
            "tooltip": "<html><body><p></p></body></html>",
        },
        "AWG - 0 - GENERATOR - GEN_FUNC - EXECUTEFUNC": {
            "datatype": "BOOLEAN",
            "group": "AWG - 0 - GEN_FUNC",
            "label": "EXECUTEFUNC",
            "permission": "WRITE",
            "section": "AWG - 0",
            "set_cmd": "AWG - 0 - " "GEN_FUNC",
            "tooltip": "<html><body><p></p></body></html>",
        },
        "AWG - 1 - CHS - COOL_FUNCTION2 - EXECUTEFUNC": {
            "datatype": "BOOLEAN",
            "group": "AWG - 1 - " "COOL_FUNCTION2",
            "label": "EXECUTEFUNC",
            "permission": "WRITE",
            "section": "AWG - 1",
            "set_cmd": "AWG - 1 - " "COOL_FUNCTION2",
            "tooltip": "<html><body><p></p></body></html>",
        },
        "AWG - 1 - COOL_FUNCTION - EXECUTEFUNC": {
            "datatype": "BOOLEAN",
            "group": "AWG - 1 - COOL_FUNCTION",
            "label": "EXECUTEFUNC",
            "permission": "WRITE",
            "section": "AWG - 1",
            "set_cmd": "AWG - 1 - COOL_FUNCTION",
            "tooltip": "<html><body><p></p></body></html>",
        },
        "AWG - 1 - GENERATOR - GEN_FUNC - EXECUTEFUNC": {
            "datatype": "BOOLEAN",
            "group": "AWG - 1 - GEN_FUNC",
            "label": "EXECUTEFUNC",
            "permission": "WRITE",
            "section": "AWG - 1",
            "set_cmd": "AWG - 1 - " "GEN_FUNC",
            "tooltip": "<html><body><p></p></body></html>",
        },
        "DEVICE - ACTIVATE - EXECUTEFUNC": {
            "datatype": "BOOLEAN",
            "group": "DEVICE - ACTIVATE",
            "label": "EXECUTEFUNC",
            "permission": "WRITE",
            "section": "DEVICE",
            "set_cmd": "DEVICE - ACTIVATE",
            "tooltip": "<html><body><p></p></body></html>",
        },
    }
