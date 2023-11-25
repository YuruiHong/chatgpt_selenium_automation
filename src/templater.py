from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


def get_prompt(file, context):
    template = env.get_template(file)
    return template.render(context)
