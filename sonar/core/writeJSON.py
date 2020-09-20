import copy
import re
import json
from .include.utilities import printError

# writeJSONPacket
# This function converts a YAML command into its equivalent JSON.


def writeJSONPacket(
    parallelSection_json,
    packet,
    vectorIndex,
    parallelIndex,
    signals_in,
    signals_out,
    interface_in,
    interface_out,
    usedInterfaces,
    counters,
):
    signal_json = {"type": "signal", "interface": "", "value": 0, "id": ""}
    # regex_int_str = re.compile("([0-9]+)([a-z]+)")
    regex_int_str = re.compile(r"([0-9]+([\.][0-9]+)*)([a-z]+)")

    if "macro" in packet:
        if packet["macro"] == "INIT_SIGNALS":
            for signal in signals_in:
                cur_signal_json = copy.deepcopy(signal_json)
                if "type" in signal:
                    cur_signal_json["type"] = "signal_" + signal["type"]
                cur_signal_json["interface"] = signal["name"]
                cur_signal_json["id"] = (
                    str(vectorIndex)
                    + "_"
                    + str(parallelIndex)
                    + "_"
                    + "init_"
                    + signal["name"]
                )
                parallelSection_json["data"].append(cur_signal_json)
            for interface in interface_in:
                if interface["connection_mode"] == "native":
                    currInterface = usedInterfaces[interface["type"]]
                    for channel in interface["channels"]:
                        if channel["type"] in currInterface.master_output_channels:
                            cur_signal_json = copy.deepcopy(signal_json)
                            cur_signal_json["type"] = "signal_" + interface["name"]
                            cur_signal_json["interface"] = (
                                interface["name"] + "_" + channel["type"]
                            )
                            cur_signal_json["id"] = (
                                str(vectorIndex)
                                + "_"
                                + str(parallelIndex)
                                + "_"
                                + "init_"
                                + cur_signal_json["interface"]
                            )
                            parallelSection_json["data"].append(cur_signal_json)
            for interface in interface_out:
                if interface["connection_mode"] == "native":
                    currInterface = usedInterfaces[interface["type"]]
                    for channel in interface["channels"]:
                        if channel["type"] in currInterface.master_input_channels:
                            cur_signal_json = copy.deepcopy(signal_json)
                            cur_signal_json["type"] = "signal_" + interface["name"]
                            cur_signal_json["interface"] = (
                                interface["name"] + "_" + channel["type"]
                            )
                            cur_signal_json["id"] = (
                                str(vectorIndex)
                                + "_"
                                + str(parallelIndex)
                                + "_"
                                + "init_"
                                + cur_signal_json["interface"]
                            )
                            parallelSection_json["data"].append(cur_signal_json)
        elif packet["macro"] == "END":
            cur_signal_json = copy.deepcopy(signal_json)
            cur_signal_json["type"] = "end"
            cur_signal_json["value"] = vectorIndex
            cur_signal_json["interface"] = "Vector_" + str(vectorIndex)
            cur_signal_json["id"] = (
                str(vectorIndex) + "_" + str(parallelIndex) + "_" + "end"
            )
            parallelSection_json["data"].append(cur_signal_json)
    # TODO support other units. Right now, template only supports ns
    elif "delay" in packet:
        m = regex_int_str.match(str(packet["delay"]))
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json["type"] = "delay"
        cur_signal_json["interface"] = str(m.group(3))
        if m.group(3) not in ["fs", "ps", "ns", "us", "ms", "s"]:
            printError(1, "Unknown time format: " + m.group(3))
            exit(1)
        cur_signal_json["value"] = str(m.group(1))
        cur_signal_json["id"] = (
            str(vectorIndex)
            + "_"
            + str(parallelIndex)
            + "_"
            + "delay_"
            + str(counters["delayCounter"])
        )
        counters["delayCounter"] += 1
        parallelSection_json["data"].append(cur_signal_json)
    elif "signal" in packet:
        for signal in packet["signal"]:
            cur_signal_json = copy.deepcopy(signal_json)
            cur_signal_json["interface"] = signal["name"]
            cur_signal_json["value"] = signal["value"]
            cur_signal_json["id"] = (
                str(vectorIndex)
                + "_"
                + str(parallelIndex)
                + "_"
                + "init_"
                + signal["name"]
            )
            parallelSection_json["data"].append(cur_signal_json)
    elif "display" in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json["type"] = "display"
        cur_signal_json["interface"] = '"' + packet["display"] + '"'
        cur_signal_json["id"] = (
            str(vectorIndex)
            + "_"
            + str(parallelIndex)
            + "_"
            + "display_"
            + str(counters["displayCounter"])
        )
        counters["displayCounter"] += 1
        parallelSection_json["data"].append(cur_signal_json)
    elif "call_dut" in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json["type"] = "call_dut"
        cur_signal_json["interface"] = "NULL"
        cur_signal_json["id"] = "NULL"
        cur_signal_json["value"] = packet["call_dut"]
        parallelSection_json["data"].append(cur_signal_json)
    elif "timestamp" in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json["type"] = "timestamp"
        cur_signal_json["interface"] = packet["timestamp"]
        cur_signal_json["id"] = (
            str(vectorIndex)
            + "_"
            + str(parallelIndex)
            + "_"
            + "timestamp_"
            + str(counters["timestampCounter"])
        )
        counters["timestampCounter"] += 1
        parallelSection_json["data"].append(cur_signal_json)
    elif "flag" in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json["type"] = "flag"
        if "set_flag" in packet["flag"]:
            cur_signal_json["interface"] = "set"
            cur_signal_json["value"] = packet["flag"]["set_flag"]
        else:
            cur_signal_json["interface"] = "clear"
            cur_signal_json["value"] = packet["flag"]["clear_flag"]
        cur_signal_json["id"] = (
            str(vectorIndex)
            + "_"
            + str(parallelIndex)
            + "_"
            + "flag_"
            + str(counters["flagCounter"])
        )
        counters["flagCounter"] += 1
        parallelSection_json["data"].append(cur_signal_json)
    elif "wait" in packet:
        cur_signal_json = copy.deepcopy(signal_json)
        cur_signal_json["type"] = "wait"
        cur_signal_json["interface"] = packet["wait"]["key"]
        cur_signal_json["id"] = (
            str(vectorIndex)
            + "_"
            + str(parallelIndex)
            + "_"
            + "wait_"
            + str(counters["waitCounter"])
        )
        if "value" in packet["wait"]:
            cur_signal_json["value"] = packet["wait"]["value"]
        else:
            cur_signal_json["value"] = 0
        counters["waitCounter"] += 1
        parallelSection_json["data"].append(cur_signal_json)
    elif "interface" in packet:
        currInterface = usedInterfaces[packet["interface"]["type"]]
        cur_interface_json = copy.deepcopy(currInterface.json_struct)
        cur_interface_json["interface"] = packet["interface"]["name"]
        for interface in interface_in:
            if interface["name"] == cur_interface_json["interface"]:
                cur_interface_json = currInterface.json_top(
                    cur_interface_json, interface
                )
        for interface in interface_out:
            if interface["name"] == cur_interface_json["interface"]:
                cur_interface_json = currInterface.json_top(
                    cur_interface_json, interface
                )
        cur_interface_json["id"] = (
            str(vectorIndex)
            + "_"
            + str(parallelIndex)
            + "_"
            + cur_interface_json["interface"]
            + "_"
            + str(counters["interfaceCounter"])
            + "_"
        )
        counters["interfaceCounter"] += 1
        for payload in packet["interface"]["payload"]:
            payloadCopy = payload.copy()
            payloadCopy = currInterface.json_payload(payloadCopy)
            cur_interface_json["payload"].append(payloadCopy)
        parallelSection_json["data"].append(cur_interface_json.copy())
    else:
        printError(1, "Unknown packet type: ")
        print(packet)
        exit(1)

    return counters


# writeJSON
# This function converts the YAML test vectors to JSON and calls any interface
# specific functions to fill in the JSON structs
def writeJSON(
    testVectors,
    dataFile,
    signals_in,
    signals_out,
    interface_in,
    interface_out,
    usedInterfaces,
):
    parallelNum = 0
    json_dict = {}
    json_dict["data"] = []

    # generate JSON file
    for vectorIndex, vector in enumerate(testVectors):
        if len(vector) > parallelNum:
            parallelNum = len(vector)
        testVector_json = {}
        testVector_json["data"] = []
        json_dict["data"].append(testVector_json)
        for parallelIndex, thread in enumerate(vector):
            parallelSection_json = {}
            parallelSection_json["data"] = []
            testVector_json["data"].append(parallelSection_json)
            counters = {}
            counters["delayCounter"] = 0
            counters["interfaceCounter"] = 0
            counters["displayCounter"] = 0
            counters["waitCounter"] = 0
            counters["timestampCounter"] = 0
            counters["flagCounter"] = 0
            for packet in thread:
                counters = writeJSONPacket(
                    parallelSection_json,
                    packet,
                    vectorIndex,
                    parallelIndex,
                    signals_in,
                    signals_out,
                    interface_in,
                    interface_out,
                    usedInterfaces,
                    counters,
                )

    # for vectorIndex, testVector in enumerate(testVectors):
    #     if len(testVector['Test_Vector_' + str(vectorIndex)]) > parallelNum:
    #         parallelNum = len(testVector['Test_Vector_' + str(vectorIndex)])
    #     testVector_json = {}
    #     testVector_json['data'] = []
    #     json_dict['data'].append(testVector_json)
    #     testVectorInst = testVector['Test_Vector_' + str(vectorIndex)]
    #     for parallelIndex, parallelSection in enumerate(testVectorInst):
    #         parallelSection_json = {}
    #         parallelSection_json['data'] = []
    #         testVector_json['data'].append(parallelSection_json)
    #         counters = {}
    #         counters['delayCounter'] = 0
    #         counters['interfaceCounter'] = 0
    #         counters['displayCounter'] = 0
    #         counters['waitCounter'] = 0
    #         counters['timestampCounter'] = 0
    #         counters['flagCounter'] = 0
    #         for packet in parallelSection['Parallel_Section_' + str(parallelIndex)]:
    #             counters = writeJSONPacket(parallelSection_json, packet, vectorIndex, \
    #                 parallelIndex, signals_in, signals_out, interface_in, \
    #                 interface_out, usedInterfaces, counters)

    json.dump(json_dict, dataFile, indent=2)
    return parallelNum
