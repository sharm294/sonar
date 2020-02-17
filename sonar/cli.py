import logging
import os
import shelve

import sonar.database as database
from sonar.include import ReturnValue, Constants, DotDict

logger = logging.getLogger(__name__)


def handle_activate(args):
    print(args.profile)
    return ReturnValue.SONAR_OK


def handler_env_add(args):
    if args.type not in vars(database.Environment()):
        logger.error(f"{args.type} is not a valid type. See sonar env add --help")
        return ReturnValue.SONAR_INVALID_ARG

    with shelve.open(Constants.SONAR_DATABASE) as db:
        environment = db["env"]
        _dict = getattr(environment, args.type)
        if args.type in ["cad_tool", "sim_tool", "hls_tool"]:
            if len(args.arg) != 3:
                logger.error(
                    f"Three args are required to add tools: executable version script"
                )
                return ReturnValue.SONAR_INVALID_NUMBER_OF_ARGS
            value = database.Tool(args.arg[0], args.arg[1], args.arg[2])
        else:
            value = args.arg[0]
        _dict[args.ID] = value
        setattr(environment, args.type, _dict)
        db["env"] = environment

    return ReturnValue.SONAR_OK


def handler_env_remove(args):
    if args.type not in vars(database.Environment()):
        logger.error(f"{args.type} is not a valid type. See sonar env remove --help")
        return ReturnValue.SONAR_INVALID_ARG

    db = shelve.open(Constants.SONAR_DATABASE)

    environment = db["env"]
    _dict = getattr(environment, args.type)
    del _dict[args.name]
    setattr(environment, args.type, _dict)
    db["env"] = environment

    db.close()
    return ReturnValue.SONAR_OK


def handler_env_edit(args):
    if args.type not in vars(database.Environment()):
        logger.error(f"{args.type} is not a valid type. See sonar env remove --help")
        return ReturnValue.SONAR_INVALID_ARG

    db = shelve.open(Constants.SONAR_DATABASE)

    environment = db["env"]
    _dict = getattr(environment, args.type)
    _dict[args.name] = args.value
    setattr(environment, args.type, _dict)
    db["env"] = environment

    db.close()
    return ReturnValue.SONAR_OK


def handler_env_show(args):
    db = shelve.open(Constants.SONAR_DATABASE)
    environment = db["env"]
    print(environment)
    db.close()
    return ReturnValue.SONAR_OK


def handler_env_clear(args):
    db = shelve.open(Constants.SONAR_DATABASE)
    db["env"] = database.Environment()
    db.close()
    return ReturnValue.SONAR_OK


def handle_init(args):
    os.makedirs(Constants.SONAR_DIRECTORY, exist_ok=True)

    retval = handler_env_clear(args)

    return retval


def handler_init_vivado(args):
    xilinx_path = os.path.abspath(args.path)

    vivado_path = os.path.join(xilinx_path, "Vivado")
    if not os.path.exists(vivado_path):
        logger.error(f"{xilinx_path} does not contain a 'Vivado' directory")
        return ReturnValue.SONAR_NONEXISTENT_PATH

    vivado_versions = os.listdir(vivado_path)
    for version in vivado_versions:
        for tool in ["cad_tool", "sim_tool", "hls_tool"]:
            args = DotDict(
                {
                    "arg": ["vivado", version, f"source setup_vivado.sh {version}"],
                    "type": tool,
                    "ID": f"vivado_{version}",
                }
            )
            handler_env_add(args)
