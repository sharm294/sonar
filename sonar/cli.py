import logging
import os
import shelve

import sonar.database as database
from sonar.include import ReturnValue, Constants

logger = logging.getLogger(__name__)


def handle_activate(args):
    print(args.profile)
    return ReturnValue.SONAR_OK


def handler_env_add(args):
    if args.type not in vars(database.Environment()):
        logger.error(f"{args.type} is not a valid type. See sonar env add --help")
        return ReturnValue.SONAR_INVALID_ARG

    db = shelve.open(Constants.SONAR_DATABASE)

    environment = db["env"]
    _dict = getattr(environment, args.type)
    _dict[args.name] = args.value
    setattr(environment, args.type, _dict)
    db["env"] = environment

    db.close()
    return ReturnValue.SONAR_OK


def handler_env_remove(args):
    if args.type not in vars(database.Environment()):
        logger.error(f"{args.type} is not a valid type. See sonar env remove --help")
        return ReturnValue.SONAR_INVALID_ARG

    db = shelve.open(Constants.SONAR_DATABASE)

    environment = db["env"]
    _dict = getattr(environment, args.type)
    print(_dict)
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


def handle_init(args):
    os.makedirs(Constants.SONAR_DIRECTORY, exist_ok=True)

    db = shelve.open(Constants.SONAR_DATABASE)
    db["env"] = database.Environment()
    db.close()

    return ReturnValue.SONAR_OK
