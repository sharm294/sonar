#!/usr/bin/python2.7
import sys
import os.path
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from interfaceTransaction import hls_test_epoch_collection
from solutionImporter import solution_importer
from hlsTestVectorToSonar import hlt_to_sonar_translator




def generate_sonar_from_high_level_test(solution_json_path, solution_high_level_test_json_path, output_sonar_json_path):
    hls_test_epochs_object = hls_test_epoch_collection.build_from_file(solution_high_level_test_json_path)

    (dut_module_name, dut_interfaces) = solution_importer.import_json_to_dut_name_and_interfaces(solution_json_path)

    output_sonar_json_file_handle = open(output_sonar_json_path, "w+")
    hlt_to_sonar_translator.write_hls_test_epochs_to_sonar_json_file(output_sonar_json_file_handle, hls_test_epochs_object, dut_interfaces, dut_module_name)

if __name__=="__main__":
    print "Running hlt to sonar translator"
    num_args = len(sys.argv)
    solution_json_path = sys.argv[1]
    solution_high_level_test_json_path = sys.argv[2]
    output_sonar_json_path = sys.argv[3]
    if (not os.path.isfile(solution_json_path)):
        print "argument 1 is not a valid solution json path: " + solution_json_path
        exit -1

    if (not os.path.isfile(solution_high_level_test_json_path)):
        print "argument 1 is not a valid solution_high_level_test_json_path: " + solution_high_level_test_json_path
        exit -1

    generate_sonar_from_high_level_test(solution_json_path, solution_high_level_test_json_path, output_sonar_json_path)

    print "Exiting with value 0"
    exit(0)