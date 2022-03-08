from enum import Enum
from lib2to3.pytree import Base
import typing as t
import pytest

from zhinst.labber.generator import function_section
from zhinst.labber.generator.function_section import FunctionParser, node_indexes
from zhinst.toolkit.nodetree import Node
from zhinst.toolkit.driver.nodes.awg import AWG


def test_function_to_group_func_replace():
    r = function_section.function_to_group(AWG.load_sequencer_program, "t")
    assert r == [
        {
            "datatype": "PATH",
            "datatype": "STRING",
            "group": "T - LOAD_SEQUENCER_PROGRAM",
            "label": "SEQUENCER_PROGRAM",
            "permission": "WRITE",
            "section": "T",
            "tooltip": "<html><body><p>Sequencer program to be "
            "uploaded</p></body></html>",
        },
        {
            "datatype": "DOUBLE",
            "def_value": "100.0",
            "group": "T - LOAD_SEQUENCER_PROGRAM",
            "label": "TIMEOUT",
            "permission": "WRITE",
            "section": "T",
            "tooltip": "<html><body><p>Maximum time to wait for the compilation on the "
            "device in seconds.</p></body></html>",
        },
        {
            "datatype": "BUTTON",
            "group": "T - LOAD_SEQUENCER_PROGRAM",
            "label": "EXECUTEFUNC",
            "section": "T",
            "tooltip": "<html><body><p>Compiles the current SequenceProgram on the AWG "
            "Core.</p></body></html>",
        },
    ]


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
