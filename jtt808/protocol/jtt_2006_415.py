from enum import Enum, unique


@unique
class LicensePateColor(Enum):
    """
    1    蓝色    按照JT/T415-2006的5.4.12
    2    黄色    按照JT/T415-2006的5.4.12
    3    黑色    按照JT/T415-2006的5.4.12
    4    白色    按照JT/T415-2006的5.4.12
    9    其他    按照JT/T415-2006的5.4.12
    """
    未知 = 0
    蓝色 = 1
    黄色 = 2
    黑色 = 3
    白色 = 4
    其他 = 9

if __name__ == '__main__':
    print(LicensePateColor(1))