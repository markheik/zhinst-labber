from collections import defaultdict

from zhinst.toolkit.driver.nodes.generator import Generator
from zhinst.toolkit.driver.devices.base import BaseInstrument
from zhinst.toolkit.driver.devices.shfqa import SHFScope
from zhinst.toolkit.driver.nodes.awg import AWG
from zhinst.toolkit.driver.modules.shfqa_sweeper import SHFQASweeper
from zhinst.toolkit.driver.nodes.readout import Readout
from zhinst.labber.generator.helpers import tooltip


NUMBER_OF_WAVEFORMS_TO_DISPLAY = 16

_IGNORED_FUNCTIONS_NORMAL = []
_IGNORED_FUNCTIONS_ADVANCED = [
    BaseInstrument.check_compatibility,
    BaseInstrument.get_streamingnodes,
    BaseInstrument.get_as_event,
    BaseInstrument.set_transaction,
    SHFQASweeper.get_result,
    SHFQASweeper.plot,
    Readout.read_integration_weights,
    Generator.read_from_waveform_memory,
    SHFScope.configure,
    AWG.read_from_waveform_memory
]

IGNORED_FUNCTIONS = {
    'NORMAL': _IGNORED_FUNCTIONS_NORMAL + _IGNORED_FUNCTIONS_ADVANCED,
    'ADVANCED': _IGNORED_FUNCTIONS_ADVANCED
}

# Ignore everything by replacing '*' to channels:
# Example: '/STATS/*/PHYSICAL/VOLTAGES/*'

# NAME. UNIT SAMPLE; #
_IGNORED_NODES = {
    'NORMAL': defaultdict(list, **{
        'SHFQA': [
            '/QACHANNELS/*/GENERATOR/WAVEFORMS/*/LENGTH',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/MEMORYUSAGE',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/STATUS',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/TRIGGERED',
            '/QACHANNELS/*/GENERATOR/ELF/*'
        ],
        'SHFQA_SWEEPER': [
            '/PLOT/*'
        ],
        'HDAWG': [
            '/AWGS/*/ELF/*',
            '/AWGS/*/SEQUENCER/MEMORYUSAGE',
            '/AWGS/*/SEQUENCER/STATUS',
            '/AWGS/*/SEQUENCER/TRIGGERED',
        ],
        'AWG': [],
        'COMMON': [
            '/STATS/*',
            '/STATUS/*',
            '/SYSTEM/ACTIVEINTERFACE*',
            '/SYSTEM/BOARDREVISIONS/*',
            '/SYSTEM/FPGAREVISION',
            '/SYSTEM/NICS/*',
            '/SYSTEM/PROPERTIES/*'
        ],
    }),
    'ADVANCED': defaultdict(list, **{
        'AWG': [
            '/ELF/*'
        ],
        'COMMON': [
            '/FEATURES/*'
        ],
        'SHFQA': [],
    })
}

# Example:
# _REPLACED_NODES = {
#     '/EXAMPLE/*/NODE/VALUE': {
#         'DATATYPE': 'PATH',
#         'UNIT': 'AMPLITUDE'
#     }
# }
_REPLACED_NODES = {
    'SHFQA': {
        '/QACHANNELS/*/GENERATOR/Waveforms/*/Wave': {
            'datatype': 'VECTOR_COMPLEX'
        },
    },
    'HDAWG': {
        '*/COMMANDTABLE/DATA': {
            'datatype': 'STRING'
        },
        '*/IMP50': {
            'datatype': 'BOOLEAN'
        }
    }
}

# First will be executed if match is found
NODE_SECTIONS = {
    'SHFQA': {
        '/QACHANNELS/*/INPUT*': 'QA Setup',
        '/QACHANNELS/*/GENERATOR*': 'Generator',
        '/QACHANNELS/*/READOUT*': 'QA Result',
        '/QACHANNELS/*/TRIGGERS/*': 'Input - Output',
        '/SCOPES/*': 'Scopes',
        '/DIOS/*': 'Input - Output',
        '/QACHANNELS/*': 'QA Setup',
        '/SCOPES/TRIGGER/*': 'Input - Output',
        '/SYSTEM/CLOCKS/*': 'Input - Output'
    },
    'HDAWG': {
        '/AWGS/*/DIO/*': 'DIO',
        '/DIOS/*': 'DIO',
        '/OSC/*': 'Oscillators',
        '/AWGS/*/OUTPUTS/*': 'Outputs',
        '/AWGS/*': 'AWG Sequencer',
        '/SINES/*': 'Sine Generator',
    }
}

# First will be executed if match is found
NODE_GROUPS = {
    'SHFQA': {
        '/QACHANNELS/0/*': 'QA Channel 0',
        '/QACHANNELS/1/*': 'QA Channel 1',
        '/QACHANNELS/2/*': 'QA Channel 2',
        '/QACHANNELS/3/*': 'QA Channel 3',
        '/QACHANNELS/4/*': 'QA Channel 4',
        '/QACHANNELS/5/*': 'QA Channel 5',
        '/QACHANNELS/6/*': 'QA Channel 6',
        '/QACHANNELS/7/*': 'QA Channel 7',
        '/SCOPES/0/*': 'Scope 0',
        '/SCOPES/1/*': 'Scope 1',
        '/SCOPES/2/*': 'Scope 2',
        '/SCOPES/3/*': 'Scope 3',
    }
}


REPLACED_FUNCTIONS = {
    Generator.load_sequencer_program: {
        'sequencer_program': {
            'datatype': 'PATH',
            'set_cmd': '*.csv',
        }
    },
    SHFScope.read: {
        'Executefunc': {
            'datatype': 'BUTTON',
        },
        'Result 0': {
            'label': "RESULT 0",
            'datatype': "VECTOR_COMPLEX",
            "show_in_measurement_dlg": "True",
        },
        'Result 1': {
            'label': "RESULT 1",
            'datatype': "VECTOR_COMPLEX",
            "show_in_measurement_dlg": "True"
        },
        'Result 2': {
            'label': "RESULT 2",
            'datatype': "VECTOR_COMPLEX",
            "show_in_measurement_dlg": "True",
            'dev_type': ['SHFQA4']
        },
        'Result 3': {
            'label': "RESULT 3",
            'datatype': "VECTOR_COMPLEX",
            "show_in_measurement_dlg": "True",
            'dev_type': ['SHFQA4']
        }
    },
    SHFQASweeper.run: {
        'Executefunc': {
            'datatype': 'BUTTON'
        },
        'Result': {
            'datatype': 'VECTOR',
            'label': 'Result',
            'show_in_measurement_dlg': 'True'
        }
    },
    SHFQASweeper.get_offset_freq_vector: {
        'Executefunc': {
            'datatype': 'BUTTON'
        },
        'Frequency points': {
            'datatype': 'VECTOR',
            'label': 'Frequency points',
            'permission': 'READ',
            'show_in_measurement_dlg': 'True'
        }
    },
    Generator.write_to_waveform_memory: {
        'Pulses': {
            'datatype': 'PATH',
            'set_cmd': '*.csv',
            'label': 'Pulses'
        },
    },
    AWG.write_to_waveform_memory: {
        'waveforms': {},
        'indexes': {},
        'Waves0': {
            'datatype': 'PATH',
            'set_cmd': '*.csv',
            'label': 'Waves0',
            'tooltip': tooltip('Waveforms 0')
        },
        'Waves1': {
            'datatype': 'PATH',
            'set_cmd': '*.csv',
            'label': 'Waves1',
            'tooltip': tooltip('Waveforms 1')
        },
        'Markers': {
            'datatype': 'PATH',
            'set_cmd': '*.csv',
            'label': 'Markers',
            'tooltip': tooltip('Markers')
        },
    }
}

REPLACED_NODES = defaultdict(dict, **_REPLACED_NODES)
IGNORED_NODES = defaultdict(list, **_IGNORED_NODES)
