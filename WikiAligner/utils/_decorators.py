import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        rv = func(*args, **kwargs)
        print('Running time: ', time.time() - start)
        return rv

    return wrapper