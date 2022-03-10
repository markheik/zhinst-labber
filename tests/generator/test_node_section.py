import pytest

from zhinst.labber.generator.node_section import NodeSection


node_dict = {
    "Node": "/DEV12018/QACHANNELS/0/CENTERFREQ",
    "Description": "The Center Frequency of the analysis band.",
    "Properties": "Read, Write, Setting",
    "Type": "Double",
    "Unit": "Hz",
}

node_dict_enum = {
    "Node": "/DEV12018/QACHANNELS/0/OUTPUT/FILTER",
    "Description": "Reads the selected analog filter before the Signal Output.",
    "Properties": "Read",
    "Type": "Integer (enumerated)",
    "Unit": "None",
    "Options": {
        "0": '"lowpass_1500": Low-pass filter of 1.5 GHz.',
        "1": '"lowpass_3000": Low-pass filter of 3 GHz.',
        "2": '"bandpass_3000_6000": Band-pass filter between 3 GHz - 6 GHz',
        "3": '"bandpass_6000_10000": Band-pass filter between 6 GHz - 10 GHz',
    },
}

@pytest.mark.skip(reason='Refactoring')
def test_node_section_no_enum():
    obj = NodeSection(node_dict)
    assert obj.as_dict() == {
        'QACHANNELS - 0 - CENTERFREQ': {
            "datatype": "DOUBLE",
            "get_cmd": "QACHANNELS/0/CENTERFREQ",
            "group": "QA Channel 0",
            "label": "QACHANNELS - 0 - CENTERFREQ",
            "permission": "BOTH",
            "section": "QA Setup",
            "set_cmd": "QACHANNELS/0/CENTERFREQ",
            "tooltip": "<html><body><p>The Center Frequency of the analysis "
            "band.</p><p><b>QACHANNELS/0/CENTERFREQ</b></p></body></html>",
            "unit": "Hz",
        }
    }

@pytest.mark.skip(reason='Refactoring')
def test_node_section_enum():
    obj = NodeSection(node_dict_enum)
    assert obj.as_dict() == {
            "QACHANNELS - 0 - OUTPUT - FILTER": {
                "datatype": "DOUBLE",
                "get_cmd": "QACHANNELS/0/OUTPUT/FILTER",
                "group": "QA Channel 0",
                "label": "QACHANNELS - 0 - OUTPUT - FILTER",
                "permission": "READ",
                "section": "QA Setup",
                "tooltip": "<html><body><p>Reads the selected analog filter before the Signal "
                "Output.</p><p><ul><li>lowpass_1500: Low-pass filter of 1.5 "
                "GHz.</li><li>lowpass_3000: Low-pass filter of 3 "
                "GHz.</li><li>bandpass_3000_6000: Band-pass filter between 3 GHz - "
                "6 GHz</li><li>bandpass_6000_10000: Band-pass filter between 6 GHz "
                "- 10 "
                "GHz</li></ul></p><p><b>QACHANNELS/0/OUTPUT/FILTER</b></p></body></html>",
            }
        }

@pytest.mark.skip(reason='Refactoring')
def test_replace_node_ch_n():
    r = replace_node_ch_n('STATS/PHYSICAL/VOLTAGES/0')
    assert r == 'STATS/PHYSICAL/VOLTAGES/*'
    
    r = replace_node_ch_n('/STATS/0/PHYSICAL/1/VOLTAGES/0')
    assert r == '/STATS/*/PHYSICAL/*/VOLTAGES/*'
