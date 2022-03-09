import typing as t

from zhinst.labber.generator import helpers
from zhinst.labber.generator import LABBER_DELIMITER_VALUE

def test_enum_description():
    assert helpers.enum_description('tester: This tests.') == ('tester', 'This tests.')
    assert helpers.enum_description('AAsdsd123') == ('', 'AAsdsd123')


def test_to_labber_format():
    assert helpers.to_labber_format(str) == 'STRING'
    assert helpers.to_labber_format(int) == 'DOUBLE'
    assert helpers.to_labber_format(float) == 'DOUBLE'
    assert helpers.to_labber_format(dict) == 'PATH'
    assert helpers.to_labber_format(bool) == 'BOOLEAN'
    assert helpers.to_labber_format(t.Dict) == 'PATH'
    assert helpers.to_labber_format(t.List) == 'PATH'
    assert helpers.to_labber_format(t.Dict) == 'PATH'
    assert helpers.to_labber_format(None) == 'NONE'


def test_labber_delimiter():
    delim = LABBER_DELIMITER_VALUE
    s = helpers.labber_delimiter('bar', '1', 'foo')
    assert s == 'BAR' + delim + '1' + delim + 'FOO'

    s = helpers.labber_delimiter('bar')
    assert s == 'BAR'
    
    s = helpers.labber_delimiter('')
    assert s == ''


def test_delete_device_from_node_path():
    r = helpers.delete_device_from_node_path('/DEV123/FOO/0/BAR')
    assert r == '/FOO/0/BAR'

    r = helpers.delete_device_from_node_path('/FOO/0/BAR')
    assert r == '/FOO/0/BAR'
