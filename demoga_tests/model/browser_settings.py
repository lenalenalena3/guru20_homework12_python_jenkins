import os


def is_selenoid_enabled():
    use_selenoid = os.getenv('USE_SELENOID', 'false').lower() == 'true'
    return use_selenoid