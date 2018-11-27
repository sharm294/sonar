from interfaceTransaction import hls_transaction
from jsonGen.burst_interface_factory import burst_interface_factory
import binascii

class port(object):
    def __init__(self, port_name, port_type, port_width):
        self.info = {
            'name': port_name,
            'type': port_type,
            'width': port_width
        }


    def add_port_attribute(self, attribute_name, attribute_value):
        self.info[attribute_name] = attribute_value

    def get_port_attribute(self, attribute_name):
        return self.info[attribute_name]



class port_interface(object):
    
    def __init__(self):
        self.info = {
            'ports': []
        }

    
    field_type_conversions = {
        'size':int
    }

    @staticmethod
    def parse_ctype_json_for_sonar(ctype_json):
        field_mappings = {
            #"Type":"name",
            "Width":"size"
        }
        channels_for_sonar = []
        for channel_name, channel_info in ctype_json.items():
            channel_dict = {
                'name':channel_name,
                'type':channel_name.lower()
            }
            for channel_field, field_value in channel_info.items():
                if (channel_field in field_mappings):
                    sonar_field_name = field_mappings[channel_field]
                    if sonar_field_name in port_interface.field_type_conversions:
                        field_value = port_interface.field_type_conversions[sonar_field_name](field_value)
                    channel_dict[sonar_field_name] = field_value
            
            channels_for_sonar.append(channel_dict)
        
        return channels_for_sonar
            
            

    @staticmethod
    def special_field_mappings(json_field_name):
        special_mappings = {
            "ctype" : port_interface.parse_ctype_json_for_sonar
        }
        special_mapping = None
        if json_field_name in special_mappings:
            special_mapping = special_mappings[json_field_name]
        return special_mapping


    @staticmethod
    def interface_type_fields_to_get(type):
        interface_type_fields_to_get = {             # {solution json field name, sonar json field name}
            "clock": {"type": "type", "": "period"},
            "reset": {},
            "": {},
            #"axis": {"clock":"clock", "mode":"direction", "ctype":"c_struct"}
            #"s_axi_ctrl_bus"
            "axi4stream": {"type":"type", "mode":"direction", "ctype":"channels"},
            "axis": {"type":"type", "mode":"direction", "ctype":"channels"},
            "ap_fifo": {"type":"type", "fifo_type":"direction", "ctype":"channels"}
        }

        return interface_type_fields_to_get[type]



    #
    # Imports vivado solution interface json into a sonar compatible json format (stored in memory as a dict)
    #
    @staticmethod
    def import_interface_for_sonar(interface_json):
        fields_to_get = port_interface.interface_type_fields_to_get(interface_json['type'])
        interface_for_sonar = { 'name': interface_json['name']}
        for json_field_name, sonar_field_name in fields_to_get.items():
            sonar_field_value = ""
            if not(port_interface.special_field_mappings(json_field_name) == None):
                func_to_call = port_interface.special_field_mappings(json_field_name)
                sonar_field_value = func_to_call(interface_json[json_field_name])
            else:
                sonar_field_value = interface_json[json_field_name]
            
            interface_for_sonar[sonar_field_name] = sonar_field_value

        return interface_for_sonar

    @staticmethod
    def generate_interface_burst_transaction(interface_json, transaction):
        interface_constructor_hash = port_interface.import_interface_for_sonar(interface_json)
        interface_type = interface_json['type']
        interface_burst_transaction_object = burst_interface_factory.build(interface_type, interface_constructor_hash)
        functions_dict = {}
        endianness = 'little'
        ### ADD_TRANSACTION_TO_BURST
        transaction_data = transaction.data
        bytearray_transaction_data = bytearray()
        #bytearray_transaction_data.extend(binascii.unhexlify(transaction_data))
        bytearray_transaction_data.extend(transaction_data)
        return interface_burst_transaction_object.binToStream(bytearray_transaction_data, functions_dict, endianness)
        ############################
        #interface_burst_transaction_object.add_transaction_to_burst(transaction, functions_dict, endianness)
        #return interface_burst_transaction_object


    @staticmethod
    def lookup_interface_direction_from_type(type):
        interface_type_to_interface_direction_lut = {
            "ap_fifo": "fifo_type",
            "axi4stream": "mode",
            "axis": "mode",
            "reset": None,
            "clock": None,
            "ap_ctrl": None
        }
        return interface_type_to_interface_direction_lut[type]

    def set_attribute(self, attribute_name, attribute_value):
        self.info[attribute_name] = attribute_value


    def get_attribute(self, attribute_name):
        return self.info[attribute_name]

    def add_port(self, port):
        self.info['ports'].append(port.info)

    def get_ports(self):
        return self.info['ports']


    @staticmethod
    def lookup_port_direction_for_interface(interface_json):
        interface_type = interface_json['type']
        field_name = port_interface.lookup_interface_direction_from_type(interface_type)
        return interface_json[field_name]
        


    @staticmethod
    def build_interface_from_interface_json(interface_name, interface_json):
        new_interface = port_interface()

        for attribute, value in interface_json.items():
            new_interface.set_attribute(attribute, value)

        new_interface.set_attribute('name', interface_name)
        
        #interface_type = interface_json['type']
        #new_interface.set_attribute('type', interface_type)
        
        #interface_direction = port_interface.lookup_interface_direction_from_type(interface_type)
        #new_interface.set_attribute('direction', interface_direction)

        ctype = interface_json['ctype']
        for port_name, port_info in ctype.items():
            port_type = port_info['Type']
            port_width = None
            if ('Width' in port_info):
                port_width = port_info['Width']
            
            new_port = port(port_name, port_type, port_width)
            if port_width == None:
                new_port.info.pop('width')
            new_interface.add_port(new_port)

        return new_interface

        