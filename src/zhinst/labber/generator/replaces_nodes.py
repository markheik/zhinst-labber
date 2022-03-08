from zhinst.toolkit.driver.nodes.generator import Generator


REPLACED_NODES = {
    '/EXAMPLE/N/NODE/VALUE': {
        'DATATYPE': 'PATH',
        'UNIT': 'AMPLITUDE'
    }
}


REPLACED_FUNCTIONS = {
    Generator.load_sequencer_program: {
        'sequencer_program': {
            'datatype': 'PATH'
        }
    }
}
