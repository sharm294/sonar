from portInterface import port_interface
import json 

class dut_json_manipulator(object):
    
    def __init__(self):
        self.data = None

    ##
    ##
    ##
    @staticmethod
    def load_solution_data_json_file(filepath):
        solution_json_object_fp = open(filepath)
        json_object = json.load(solution_json_object_fp)
        return json_object
    
    ##
    ##
    ##
    @staticmethod
    def get_ip_interfaces_from_solution_json_object(solution_json_object):
        interfaces_json_tag = 'Interfaces'
        interface_json_list = solution_json_object[interfaces_json_tag]
        interfaces = [port_interface.build_interface_from_interface_json(interface_name, interface_json) \
                        for interface_name, interface_json in interface_json_list.items()]
        return interfaces


    ##
    ##
    ##
    @staticmethod
    def get_interface(interface_list, interface_name):
        return interface_list[interface_name]


    ##
    ## E.g. example attribute names include "type" "mode" "port_prefix" "has_tready" "port_width" "ctype"
    ##
    @staticmethod
    def get_interface_attribute(interface, attribute_name):
        return interface[attribute_name]


    ##
    ## Returns a list of names (all lowercase) of each port found in this interface
    ##
    @staticmethod
    def getInterfacePortsNames(interface):
        ctypes = interface["ctype"]
        port_names = list(ctypes.keys())
        return [port_name.lower() for port_name in port_names]