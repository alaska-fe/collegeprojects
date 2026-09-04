import datetime, os, platform, pwd

def sbor_info_pc():
    try:
        username = os.getlogin()
    except OSError:
        username = os.getenv('USER') or os.getenv('LOGNAME') or 'unknown'

    pc_data = f'{username}-{platform.node()}-{platform.processor()}'
    return abs(hash(pc_data))

def random_gen(first, second):
    if not isinstance(first, int) or not isinstance(second, int):
        raise TypeError("оба числа должны быть int")
    if first == second:
        return first
    if first > second:
        first, second = second, first

    time_seed = int(str(datetime.datetime.now())[-6:])
    hw_seed = sbor_info_pc()
    combined_seed = time_seed ^ hw_seed
    dynamic_range = second - first + 1
    pseudo_random = (combined_seed * 1103515245 + 12345) % 2 ** 31
    result = first + (pseudo_random % dynamic_range)
    return result

print(random_gen(2, 10000))
