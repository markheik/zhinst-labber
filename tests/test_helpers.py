import typing as t

from zhinst.labber.generator import helpers


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