# import sys
# import os.path
# import time
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
from jsonGen.module import Module
from dut_json_manipulator import dut_json_manipulator

class solution_importer(object):

    @staticmethod
    def import_json_to_dut_name_and_interfaces(solution_json_file_path):
        #dut_json_manipulator.get_ip_interfaces_from_solution_json_object(dut_solution_json)
        solution_json = dut_json_manipulator.load_solution_data_json_file(solution_json_file_path)
        dut_interfaces = dut_json_manipulator.get_ip_interfaces_from_solution_json_object(solution_json)

        return (solution_json['Top'], dut_interfaces)


