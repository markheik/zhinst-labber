import jinja2
import black
import autoflake


def generate_labber_device_driver_code(classname, settings_file):
    data = {
        "class": {
            'name': classname
            },
        'settings_file': settings_file
    }

    templateLoader = jinja2.FileSystemLoader(searchpath='')
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("templates/device_template.py.j2")
    result = template.render(data)
    result = black.format_str(result, mode=black.FileMode())
    result = autoflake.fix_code(result, remove_all_unused_imports=True)
    return result
