DEBUG = False


def enable_debug():
    global DEBUG
    DEBUG = True


def printd(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)
