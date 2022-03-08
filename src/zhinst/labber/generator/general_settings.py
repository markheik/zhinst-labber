def general_settings_device(config, device):
    section = 'General settings'
    config.add_section(section)
    config.set(section, "name", f'Zurich Instruments {device.device_type}')
    config.set(section, "version", f'0.1')
    config.set(section, "driver_path", f'Zurich_Instruments_{device.device_type}')
    config.set(section, "interface", f'Other')
    config.set(section, "startup", f'Do nothing')


def general_settings_dataserver(config):
    section = 'General settings'
    config.add_section(section)
    config.set(section, "name", f'Zurich Instruments DataServer')
    config.set(section, "version", '0.1')
    config.set(section, "driver_path", f'Zurich_Instruments_DataServer')
    config.set(section, "interface", f'Other')
    config.set(section, "startup", f'Do nothing')


def general_settings_module(config, module):
    section = 'General settings'
    config.add_section(section)
    config.set(section, "name", f'Zurich Instruments {module.upper()} Module')
    config.set(section, "version", f'0.1')
    config.set(section, "driver_path", f'Zurich_Instruments_{module.upper()}_Module')
    config.set(section, "interface", f'Other')
    config.set(section, "startup", f'Do nothing')