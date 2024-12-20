import logging as log


def define_logger(verbose=1):
    """
    method which sets the verbose handler
    """
    if verbose == 0:
        level = None
    elif verbose == 1:
        level = log.INFO
    elif verbose == 2:
        level = log.DEBUG
    elif verbose == 3:
        level = log.WARNING
    else:
        raise ValueError(
            "Unknown verbose was set. 0 to disable verbose, 1 for INFO, 2 for DEBUG, 3 for WARNING."
        )

    log.basicConfig(
        format="%(levelname)s %(filename)s %(lineno)s %(message)s", level=level
    )
