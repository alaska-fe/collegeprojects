import datetime
import os
import platform
import psutil

def sbor_info_pc(humidity_param, wind_param):
    try:
        username = os.getlogin()
    except OSError:
        username = os.getenv('USERNAME') or os.getenv('USER') or os.getenv('LOGNAME') or 'unknown'
    pc_data = f'{username}-{platform.node()}-{platform.processor()}-{humidity_param}-{wind_param}'
    return abs(hash(pc_data))


def random_gen(first, second):
    if not isinstance(first, int) or not isinstance(second, int):
        raise TypeError("оба числа должны быть int")
    if first == second:
        return first
    if first > second:
        first, second = second, first

    humidity_param = psutil.virtual_memory().percent
    wind_param = psutil.cpu_percent(interval=None)

    time_seed = datetime.datetime.now().microsecond
    hw_seed = sbor_info_pc(humidity_param, wind_param)

    combined_seed = time_seed ^ hw_seed
    dynamic_range = second - first + 1
    pseudo_random = (combined_seed * 1103515245 + 12345) % (2 ** 31)
    result = first + (pseudo_random % dynamic_range)
    return result

print(random_gen(2, 4))
