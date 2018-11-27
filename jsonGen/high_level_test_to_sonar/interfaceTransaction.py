import json
import binascii

class hls_transaction(object):
    
    def __init__(self, _interface_name, _location_type, _data_value):
        self.interface_name = _interface_name

        if (_location_type == "file"):
            data_file = open(_data_value, "rb")
            self.data = data_file.read()
        elif (_location_type == "inline"):
            self.data = binascii.unhexlify(_data_value)
        else:
            self.data = None

    #"interface"
    #"data_location"
    #"data"

    @classmethod
    def build_transaction_from_json(hls_transaction, decoded_json_transaction):
        return  hls_transaction(decoded_json_transaction['interface'], \
                                decoded_json_transaction['data_location'], \
                                decoded_json_transaction['data'])


class hls_transaction_epoch(object):

    def __init__(self):
        self.transactions = []

    def add(self, hls_transaction):
        self.transactions.append(hls_transaction)

    def get(self):
        return self.transactions

    def number_of_transactions(self):
        return len(self.transactions)

    def get_interfaces_used(self):
        interface_names = {}
        for transaction in self.transactions:
            interface_names[transaction.interface_name] = transaction.interface_name
        
        return list(interface_names.keys())



class hls_test_epoch_collection(object):

    def __init__(self):
        self.test_epochs = []

    def get_transactions_from_epoch(self, epoch):
        return self.test_epochs[epoch].get()

    def number_of_epochs(self):
        return len(self.test_epochs)

    def get_epoch(self, epoch_id):
        return self.test_epochs[epoch_id]

    def add_transaction_to_epoch(self, epoch, hls_transaction):
        if (self.number_of_epochs() <= epoch):
            self.test_epochs.extend([None]*(epoch + 1 - self.number_of_epochs()))

        if (self.test_epochs[epoch] == None):
            self.test_epochs[epoch] = hls_transaction_epoch()
        
        self.test_epochs[epoch].add(hls_transaction)

    def get_interfaces_used(self):
        interface_names = {}

        for epoch in self.test_epochs:
            epoch_interfaces = epoch.get_interfaces_used()
            for epoch_interface_name in epoch_interfaces:
                interface_names[epoch_interface_name] = epoch_interface_name

        return list(interface_names.keys())


    @staticmethod
    def build_from_file(hls_test_transactions_file):
        test_json_object_fp = open(hls_test_transactions_file)
        test_as_json_object = json.load(test_json_object_fp)
        
        hls_test = hls_test_epoch_collection()

        for epoch in range(len(test_as_json_object)):
            epoch_transactions = test_as_json_object[epoch]
            for transaction_id in range(len(epoch_transactions)):
                transaction = epoch_transactions[transaction_id]
                hls_test.add_transaction_to_epoch(epoch, hls_transaction(transaction['port'], transaction['data_location'], transaction['data']))
        
        return hls_test

    