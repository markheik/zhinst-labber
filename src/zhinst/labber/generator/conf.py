from collections import defaultdict

from zhinst.toolkit.driver.nodes.generator import Generator
from zhinst.toolkit.driver.devices.base import BaseInstrument
from zhinst.toolkit.driver.devices.shfqa import SHFScope
from zhinst.toolkit.driver.modules.shfqa_sweeper import SHFQASweeper
from zhinst.toolkit.driver.nodes.readout import Readout
from zhinst.labber.generator.helpers import tooltip


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
    SHFScope.configure
]

IGNORED_FUNCTIONS = {
    'NORMAL': _IGNORED_FUNCTIONS_NORMAL + _IGNORED_FUNCTIONS_ADVANCED,
    'ADVANCED': _IGNORED_FUNCTIONS_ADVANCED
}

# Ignore everything by replacing '*' to channels:
# Example: '/STATS/*/PHYSICAL/VOLTAGES/*'

_IGNORED_NODES = {
    'NORMAL': defaultdict(list, **{
        'SHFQA': [
            '/QACHANNELS/*/GENERATOR/WAVEFORMS/*/LENGTH',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/MEMORYUSAGE',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/STATUS',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/TRIGGERED',
            '/QACHANNELS/*/GENERATOR/ELF/*'
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
        'SHFQA_SWEEPER': [
            '/PLOT/*'
        ]
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
    'SHFQA': {}
}


_EXPANDED_NODES = {
    'SHFQA': {
        '/QACHANNELS/*/GENERATOR/Waveforms/*/Wave' : [
            {
                'label': 'Wave0',
                'datatype': 'PATH',
                'set_cmd': '*.csv',
            },
            {
                'label': 'Wave1',
                'datatype': 'PATH',
                'set_cmd': '*.csv',
            },
            {
                'label': 'Markers',
                'datatype': 'PATH',
                'set_cmd': '*.csv',
            },
            {
                'label': 'To Device',
                'datatype': 'PATH',
                'set_cmd': '*.csv',
            },
        ]
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
        '/DIOS*': 'Input - Output',
        '/QACHANNELS/*': 'QA Setup',
        '/SCOPES/TRIGGER/*': 'Input - Output',
        '/SYSTEM/CLOCKS/*': 'Input - Output'
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
        'Pulses': {},
        'Wave0': {
            'datatype': 'PATH',
            'set_cmd': '*.csv',
            'label': 'Wave0',
            'tooltip': tooltip('Waveform 0')
        },
        'Wave1': {
            'datatype': 'PATH',
            'set_cmd': '*.csv',
            'label': 'Wave1',
            'tooltip': tooltip('Waveform 1')
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
