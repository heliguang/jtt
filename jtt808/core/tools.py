import time

from jtt808.core.covert import Covert


def read_bit(bytes, index, offset):
    mask = 1 << offset
    return (Covert.bytes_2_number(bytes, index, 1) & mask) >> offset


def write_bit(a_int, offset, value):
    if value == 1: # 将某一位置为1
        mask = 1 << offset
        return a_int | mask
    else:   # 将某一位清除为0
        mask = ~(1 << offset)
        return a_int & mask


def format_timestamp(timestamp, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(timestamp / 1000))


if __name__ == '__main__':
    print(read_bit(b'0x01', 0, 0))
    print(format_timestamp(int('190423172359')))
