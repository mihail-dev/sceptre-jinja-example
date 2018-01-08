from troposphere import Template, Tags, Base64, Join
from jinja2 import Environment, FileSystemLoader
import os


class SceptreTemplate(object):
    """This parent class exists in order to encapsulate functions that are
    commonly-used across various Sceptre templates.
    """
    def __init__(self):
        self.template = Template()

    def tag_resource(self, tag_dict):
        if tag_dict:
            return {"Tags": Tags(**tag_dict)}
        else:
            return {"Tags": Tags()}

    def read_from_file(self, file_path, variables):
        data = []

        path, filename = os.path.split(file_path)
        render_result = Environment(
            loader=FileSystemLoader(path)
        ).get_template(filename).render(variables)

        userdata_filepath = os.path.join(path, ".rendered_" + filename)
        with open(userdata_filepath, 'w') as userdata:
            userdata.write(render_result)

        with open(userdata_filepath, 'r') as userdata:
            for line in userdata:
                data.append(line)
        os.remove(userdata_filepath)
        return Base64(Join("", data))
