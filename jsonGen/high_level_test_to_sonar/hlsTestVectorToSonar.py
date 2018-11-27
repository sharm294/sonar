
from jsonGen.parallelSection import ParallelSection
from jsonGen.module import Module
from jsonGen.testVector import TestVector
from portInterface import port_interface
import dut_json_manipulator

class hlt_to_sonar_translator(object):

#def interface_to_burst_or_signal_transaction(interface_type):
    type_to_burst_signal_type = {
        "ap_fifo": "burst",
        "axis":"burst",
        "axi4stream":"burst",
        "s_axilite":"burst",
        "clock":"signal",
        "reset":"signal",
    }

#    return type_to_burst_signal_type[interface_type]

    @staticmethod
    def generate_signal(transaction, interface):
        print "generate_signal unimplemented"
        exit -1


    @staticmethod
    def generate_burst(transaction, interface):
        interface_type = interface['type']
        burst_transaction = None
        if (interface_type == "axis" or interface_type == "axi4stream"):
            burst_transaction = port_interface.generate_interface_burst_transaction(interface,transaction)
        elif (interface_type == "ap_fifo"):
            burst_transaction = port_interface.generate_interface_burst_transaction(interface,transaction)
        else:
            print "unsupported interface type in hlt_to_sonar_translator.generate_burst"
            exit(-1)
        
        return burst_transaction


    @staticmethod
    def add_transaction_to_parallel_section(parallel_section, transaction, dut_interfaces):
        interface_name = transaction.interface_name
        interface = next(dut_interface.info for dut_interface in dut_interfaces if (dut_interface.info['name'] == interface_name))#, None) #dut_interfaces.get(interface_name)
        interface_type = interface['type']
        burst_or_signal = hlt_to_sonar_translator.type_to_burst_signal_type[interface_type] #interface_to_burst_or_signal_transaction(interface_type)

        if (burst_or_signal == "signal"):
            parallel_section.addSignal(hlt_to_sonar_translator.generate_signal(transaction, interface))
        elif (burst_or_signal == "burst"):
            parallel_section.addBurst(hlt_to_sonar_translator.generate_burst(transaction, interface))
        else:
            exit(-1)



    @staticmethod
    def generate_interface_wait_conditions(dut_interfaces_with_transactions):
        interface_name_to_wait_condition_key_map = {}
        wait_condition_dict = {}

        #for interface_name, interface in dut_interfaces.items():
        for dut_interface in dut_interfaces_with_transactions:
            interface_name = dut_interface.info['name']
            wait_key_name = interface_name + "_tlast"
            condition = "wait(1 == " + interface_name + ".TLAST);"
            wait_condition_dict[wait_key_name] = {"key":wait_key_name, "condition": condition}

            interface_name_to_wait_condition_key_map[interface_name] = wait_key_name


        return (wait_condition_dict, interface_name_to_wait_condition_key_map)


    @staticmethod
    def calculate_highest_number_of_parallel_transactions(hls_test_epochs_object):
        most_parallel_transactions = 0
        for epoch in range(hls_test_epochs_object.number_of_epochs()):
            num_transactions_this_epoch = hls_test_epochs_object.get_epoch(epoch).number_of_transactions()# get_transactions_from_epoch(epoch))
            most_parallel_transactions = max(most_parallel_transactions, num_transactions_this_epoch)

        return most_parallel_transactions


    @staticmethod
    def generate_wait_keys_for_this_epoch(epoch, interface_waits, interface_name_to_wait_condition_key_map):
        epoch_interface_transactions = interface_waits.get_transactions_from_epoch(epoch)
        wait_keys = []
        interface_name_to_wait_statement_id_map = {}
        num_transactions = len(epoch_interface_transactions)
        for transaction_id in range(num_transactions):
            transaction = epoch_interface_transactions[transaction_id]
            transaction_interface_name = transaction.interface_name#['interface']
            interface_name_to_wait_statement_id_map[transaction_interface_name] = transaction_id
            interface_wait_key_name = interface_name_to_wait_condition_key_map[transaction_interface_name]

            wait_keys.append(interface_wait_key_name)

        return (wait_keys, interface_name_to_wait_statement_id_map)

        

    @staticmethod
    def emit_wait_keys_to_keep_list(wait_keys_list, excluded_indeces):
        indeces_to_keep = [i for i in range(len(wait_keys_list)) if i not in excluded_indeces]
        wait_statements_to_keep = [wait_keys_list[i] for i in indeces_to_keep]

        
        return wait_statements_to_keep


    @staticmethod
    def get_in_use_interfaces_in_test_epochs(dut_interfaces, hls_test_epochs_object):
        interface_names_used = hls_test_epochs_object.get_interfaces_used()
        #interfaces_used = []
        #for dut_interface in dut_interfaces:
        #    if dut_interface.info['name'] in interface_names_used:
        #        interfaces_used.append(dut_interface)
        #return interface_used
        return [dut_interface for dut_interface in dut_interfaces if dut_interface.info['name'] in interface_names_used]


    @staticmethod
    def generate_parallel_sections(hls_test_epochs_object, dut_interfaces):

        num_epochs = hls_test_epochs_object.number_of_epochs()

        most_parallel_transactions = hlt_to_sonar_translator.calculate_highest_number_of_parallel_transactions(hls_test_epochs_object)
        parallel_sections = [ParallelSection() for i in range(most_parallel_transactions + 1)]
        #parallel_section_statement_lists = []

        ## Setup clock
        last_parallel_section = ParallelSection()
        
        #last_parallel_section.addWait({"key": "mem_ready", "condition": "wait(mem_ready);"})
        last_parallel_section.addWait({"key": "ap_clk", "condition": "@(negedge ap_clk);"})
        last_parallel_section.addMacro("INIT_SIGNALS")
        last_parallel_section.addDelay("40ns")
        last_parallel_section.addSignal([{"name": "ap_rst_n", "value": 1}, {"name": "axis_output_TREADY", "value": 1}])
        parallel_sections[most_parallel_transactions] = last_parallel_section

        dut_interfaces_in_use_by_transactions = hlt_to_sonar_translator.get_in_use_interfaces_in_test_epochs(dut_interfaces, hls_test_epochs_object)

        interface_waits = hls_test_epochs_object
        (wait_condition_dict, interface_name_to_wait_condition_key_map) = hlt_to_sonar_translator.generate_interface_wait_conditions(dut_interfaces_in_use_by_transactions)

        
        for epoch in range(num_epochs):
            epoch_transactions = hls_test_epochs_object.get_transactions_from_epoch(epoch)

            (wait_keys_list, interface_name_to_wait_statement_id_map) = hlt_to_sonar_translator.generate_wait_keys_for_this_epoch(epoch, interface_waits, interface_name_to_wait_condition_key_map)

            num_transactions = len(epoch_transactions)
            num_parallel_sections_without_transactions_this_epoch = most_parallel_transactions - num_transactions

            for transaction_id in range(num_transactions):
                parallel_section_id = transaction_id
                transaction = epoch_transactions[transaction_id]

                # Generate wait statements in this parallel section to wait for all other concurrent transactions in
                # this epoch to complete
                interface_name = transaction.interface_name#['interface']
                excluded_interfaces = [interface_name_to_wait_statement_id_map[interface_name]]
                wait_keys_to_use_for_this_epoch_and_parallel_section = hlt_to_sonar_translator.emit_wait_keys_to_keep_list(wait_keys_list, excluded_interfaces)

                map(lambda wait_key: parallel_sections[parallel_section_id].addWait(wait_condition_dict[wait_key]), wait_keys_to_use_for_this_epoch_and_parallel_section)
                    # Need to go from key to wait statement

                hlt_to_sonar_translator.add_transaction_to_parallel_section(parallel_sections[parallel_section_id], transaction, dut_interfaces_in_use_by_transactions)
                
            # We need to generate wait statements for all parallel sections that did not contain transactions
            # in this epoch to prevent parallel sections from becoming sequentially out of sync (from our high level design)
            for parallel_section_id in range(num_transactions, num_parallel_sections_without_transactions_this_epoch):
                all_wait_keys_from_this_epoch = hlt_to_sonar_translator.emit_wait_keys_to_keep_list(wait_keys_list, [])

                map(parallel_sections[parallel_section_id].addWait(wait_condition_dict[wait_key])\
                    for wait_key in all_wait_keys_from_this_epoch)


        return parallel_sections

    @staticmethod
    def translate_hlt_port_field_ctype_to_sonar_dut_field(hls_port):
        ctype = hls_port['ctype']
        channels = []
        channel_field_translation_map = {
            'Width':'size'
        }
        to_int_fields = {'size'}

        for channel_name in ctype:
            channel_sonar = {'name':channel_name, 'type':channel_name.lower()}
            channel_hlt = ctype[channel_name]
            for field_key in channel_hlt:
                if field_key in channel_field_translation_map:
                    translated_key = channel_field_translation_map[field_key]
                    channel_sonar[translated_key] = channel_hlt[field_key]
                    if translated_key in to_int_fields:
                        channel_sonar[translated_key] = int(channel_sonar[translated_key])
            channels.append(channel_sonar)

        return channels

    
    @staticmethod
    def add_dut_reset_port_fields(hlt_port, sonar_port_in_progress):
        sonar_port_in_progress['direction'] = 'input'
        return sonar_port_in_progress

    @staticmethod
    def add_dut_clock_port_fields(hlt_port, sonar_port_in_progress):
        sonar_port_in_progress['period'] = '10ns' #harcoded... for now
        sonar_port_in_progress['direction'] = 'input'
        return sonar_port_in_progress

    @staticmethod
    def transform_hlt_json_interface_to_sonar_dut_port(hlt_port):
        special_field_handlers = {
            'ctype':hlt_to_sonar_translator.translate_hlt_port_field_ctype_to_sonar_dut_field
        }

        special_type_handlers = {
            'reset':hlt_to_sonar_translator.add_dut_reset_port_fields,
            'clock':hlt_to_sonar_translator.add_dut_clock_port_fields
        }

        type_field_map = {
            'axi4stream': {'type':'type', 'name':'name', 'mode':'direction', 'ctype':'channels'},
            'axis': {'type':'type', 'name':'name', 'mode':'direction', 'ctype':'channels'},
            'ap_fifo': {},
            'reset': {'type':'type', 'name':'name'},
            'clock': {'type':'type', 'name':'name'}
        }
        interface_type = hlt_port['type']
        port_field_name_mappings = type_field_map[interface_type]

        sonar_port = {}
        if interface_type in special_type_handlers:
            sonar_port = special_type_handlers[interface_type](hlt_port, sonar_port)

        for hlt_field_name in port_field_name_mappings:
            sonar_field_name = port_field_name_mappings[hlt_field_name]
            
            hlt_field = {}
            if hlt_field_name in special_field_handlers:
                hlt_field = special_field_handlers[hlt_field_name](hlt_port)
            else:
                hlt_field = hlt_port[hlt_field_name]

            sonar_port[sonar_field_name] = hlt_field

        return sonar_port


    @staticmethod
    def apply_clock_attributes_to_ports(dut_module, dut_interfaces):
        clock_interface_list = (interface.info for interface in dut_interfaces if interface.info['type'] == 'clock')
        for clock_interface in clock_interface_list:
            buses = clock_interface['buses'].split()

            ports = dut_module.ports
            for port in ports:
                if port['name'] in buses:
                    port['clock'] = clock_interface['name']
        

    @staticmethod
    def apply_cstream_and_cstruct_attributes_to_ports(dut_module, dut_interfaces):
        field_map = {
            "axi4stream" : {'c_stream':'axis_word', 'c_struct':'uaxis_l'},
            "axis" : {'c_stream':'axis_word', 'c_struct':'uaxis_l'}
        }

        for port in dut_module.ports:
            interface_type = port['type']
            if interface_type in field_map:
                port['c_stream'] = field_map[interface_type]['c_stream']
                port['c_struct'] = field_map[interface_type]['c_struct']
        


    # The format for hls_test_epochs_object is as follows (json):
    #  [
    #     [  ## All transactions in this section are run in parallel
    #         { "interface": "interface_name", "data_location": "(inline|file)", "data": "hex_data_if_inline_or_file_path" },
    #         { "interface": "interface_name2", "data_location": "(inline|file)", "data": "hex_data_if_inline_or_file_path2" }
    #     ],
    #  ]
    @staticmethod
    def generate_populated_test_module_from_hls_test_epochs(hls_test_epochs_object, dut_interfaces, dut_module_name):

        # "Module_Name" for dut and definition
        dut_module = Module(dut_module_name)
        

        # "DUT" ports
        map(lambda dut_port: dut_module.addPort(hlt_to_sonar_translator.transform_hlt_json_interface_to_sonar_dut_port(dut_port.info)), dut_interfaces)

        hlt_to_sonar_translator.apply_clock_attributes_to_ports(dut_module, dut_interfaces)
        hlt_to_sonar_translator.apply_cstream_and_cstruct_attributes_to_ports(dut_module, dut_interfaces)
        
        # Generate parallel sections and waits - then populate the module
        parallel_sections = hlt_to_sonar_translator.generate_parallel_sections(hls_test_epochs_object, dut_interfaces)
        testVector0 = TestVector()
        map(lambda parallel_section: testVector0.addSection(parallel_section), parallel_sections)
        dut_module.addVec(testVector0)


        return dut_module


    @staticmethod
    def write_hls_test_epochs_to_sonar_json_file(output_sonar_json_file_handle, hls_test_epochs_object, dut_interfaces, dut_module_name):

        # Generate the transactions
        dut_module = hlt_to_sonar_translator.generate_populated_test_module_from_hls_test_epochs(hls_test_epochs_object, dut_interfaces, dut_module_name)

        # Write the json to file
        output_sonar_json_file_handle.write(dut_module.getJSON())





