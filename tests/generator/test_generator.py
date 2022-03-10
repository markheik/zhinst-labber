from zhinst.labber.generator.generator import replace_node_ch_n


def test_replace_node_ch_n():
    r = replace_node_ch_n('STATS/PHYSICAL/VOLTAGES/0')
    assert r == 'STATS/PHYSICAL/VOLTAGES/*'
    
    r = replace_node_ch_n('/STATS/0/PHYSICAL/1/VOLTAGES/0')
    assert r == '/STATS/*/PHYSICAL/*/VOLTAGES/*'
