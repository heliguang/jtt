from jtt808.core.covert import Covert
from jtt808.core.tools import read_bit, format_timestamp
from jtt808.protocol.jtt_2006_415 import LicensePateColor
# https://github.com/cn/GB2260.py
import gb2260


def is_jtt_808(hex_string):
    is_jtt = False
    try:
        bytes = Covert.hex_string_2_bytes(hex_string)
        is_jtt = (bytes[0] == 0x7E
                      and bytes[len(bytes) - 1] == 0x7E
                      and len(bytes) >= 15)
    except Exception as e:
        print('exception:', e)
    finally:
        return is_jtt


def decode_hex_string(hex_string):
    if is_jtt_808(hex_string):
        bytes = Covert.hex_string_2_bytes(hex_string)
        if get_message_id(bytes) in decoders.keys():
            return decoders[get_message_id(bytes)](bytes)
        else:
            return {**{
                '错误': '服务器不支持该协议数据',
                '支持的消息ID列表': ''
            }, **{
                '序号:{0}'.format(index + 1): '消息ID:0x{0}'.format(id) for index, id in enumerate(decoders.keys())
            }}
    else:
        return {'错误': '文本不是部标协议'}


def get_message_id(bytes):
    return Covert.bytes_2_hex_string(bytes, 1, 2)


def is_subpackage(bytes):
    return read_bit(bytes, 3, 5) == 1


def get_message_body_index(bytes):
    if is_subpackage(bytes):
        return 17
    else:
        return 13


def get_message_body_length(bytes):
    return ((bytes[3] & 0x03) << 8) | bytes[4]


def decode_header(bytes):
    body_index = get_message_body_index(bytes)
    parameters = {
        '消息头': Covert.bytes_2_hex_string(bytes, 1, body_index - 1),
        '开始标示位': Covert.bytes_2_hex_string(bytes, 0, 1),
        '消息ID': '0x' + get_message_id(bytes),
        '消息体属性': Covert.bytes_2_hex_string(bytes, 3, 2),
        '分包': is_subpackage(bytes),
        '消息体长度': get_message_body_length(bytes),
        '终端手机号': Covert.bytes_2_hex_string(bytes, 5, 6),
        '消息流水号': Covert.bytes_2_hex_string(bytes, 11, 2),
        '结束标示位': Covert.bytes_2_hex_string(bytes, len(bytes) - 1, 1),
    }
    if is_subpackage(bytes):
        return {**parameters, **{
            '消息总包数': Covert.bytes_2_hex_string(bytes[3:5]),
            '包序号': Covert.bytes_2_hex_string(bytes[len(bytes) - 1:]),
        }}
    else:
        return parameters


def decode_0x8001(bytes):
    body_index = get_message_body_index(bytes)
    body_length = get_message_body_length(bytes)
    return {**decode_header(bytes), **{
        '含义': '平台通用应答',
        '消息体': Covert.bytes_2_hex_string(bytes, body_index, body_length),
        '应答流水号': Covert.bytes_2_number(bytes, body_index + 0, 2),
        '应答ID': Covert.bytes_2_number(bytes, body_index + 2, 2),
        '结果': Covert.bytes_2_number(bytes, body_index + 4, 1),
    }}


def decode_0x0100(bytes):
    body_index = get_message_body_index(bytes)
    body_length = get_message_body_length(bytes)
    province_id = Covert.bytes_2_number(bytes, body_index + 0, 2)
    city_id = Covert.bytes_2_number(bytes, body_index + 2, 2)

    province_id_str = str(province_id)
    format_province_id_str = ''.join(['0' for i in range(2 - len(province_id_str))]) + province_id_str
    city_id_str = str(city_id)
    format_city_id_str = ''.join(['0' for i in range(4 - len(city_id_str))]) + city_id_str

    division = gb2260.get(int(format_province_id_str + format_city_id_str))
    print('code', int(format_province_id_str + format_city_id_str))
    print('division.province', type(division.province), division.province, division.province.__str__())
    print('division.name', type(division.name))
    return {**decode_header(bytes), **{
        '含义': '终端注册',
        '消息体': Covert.bytes_2_hex_string(bytes, body_index + 0, body_length),
        '省域ID': '{0}[{1}]'.format(format_province_id_str, division.province.__str__()),
        '市县域ID': city_id_str + '[' + division.name + ']',
        '制造商ID': Covert.bytes_2_hex_string(bytes, body_index + 4, 5),
        '终端型号': Covert.bytes_2_hex_string(bytes, body_index + 9, 8),
        '终端ID': Covert.bytes_2_hex_string(bytes, body_index + 17, 7),
        '车牌颜色': Covert.bytes_2_hex_string(bytes, body_index + 24, 1) + '[' + str(LicensePateColor(Covert.bytes_2_number(bytes, body_index + 24, 1))) + ']',
        '车牌': Covert.bytes_2_hex_string(bytes, body_index + 25, body_length - 25) + '[' + bytes.fromhex(Covert.bytes_2_hex_string(bytes, body_index + 25, body_length - 25)).decode('GBK') + ']',
    }}


def decode_0x8100(bytes):
    body_index = get_message_body_index(bytes)
    body_length = get_message_body_length(bytes)
    return {**decode_header(bytes), **{
        '含义': '终端注册应答',
        '消息体': Covert.bytes_2_hex_string(bytes, body_index, body_length),
        '应答流水号': Covert.bytes_2_hex_string(bytes, body_index + 0, 2),
        '结果': Covert.bytes_2_hex_string(bytes, body_index + 2, 1),
        '鉴权码': Covert.bytes_2_hex_string(bytes, body_index + 3, body_length - 3),
    }}


def decode_0x0200(bytes):
    body_index = get_message_body_index(bytes)
    body_length = get_message_body_length(bytes)
    return {**decode_header(bytes), **{
    # return {**{
        '含义': '位置信息汇报',
        '消息体': Covert.bytes_2_hex_string(bytes, body_index, body_length),
        '报警标志': Covert.bytes_2_hex_string(bytes, body_index + 0, 4),
        '紧急报警': read_bit(bytes, body_index + 3, 0),
        '超速报警': read_bit(bytes, body_index + 3, 1),
        '疲劳报警': read_bit(bytes, body_index + 3, 2),
        '预警': read_bit(bytes, body_index + 3, 3),
        'GNSS模块故障': read_bit(bytes, body_index + 3, 4),
        'GNSS天线未接或被剪断': read_bit(bytes, body_index + 3, 5),
        'GNSS天线短路': read_bit(bytes, body_index + 3, 6),
        '终端主电源欠压': read_bit(bytes, body_index + 3, 7),

        '终端主电源掉电': read_bit(bytes, body_index + 2, 0),
        '终端LCD或显示器故障': read_bit(bytes, body_index + 2, 1),
        'TTS模块故障': read_bit(bytes, body_index + 2, 2),
        '摄像头故障': read_bit(bytes, body_index + 2, 3),

        '当天累计驾驶超时': read_bit(bytes, body_index + 1, 2),
        '超时停车': read_bit(bytes, body_index + 1, 3),
        '进出区域': read_bit(bytes, body_index + 1, 4),
        '进出路线': read_bit(bytes, body_index + 1, 5),
        '路段行驶时间不足/过长': read_bit(bytes, body_index + 1, 6),
        '线路偏离报警': read_bit(bytes, body_index + 7, 7),

        '车辆VSS故障': read_bit(bytes, body_index + 0, 0),
        '车辆油量异常': read_bit(bytes, body_index + 0, 1),
        '车辆被盗（通过车辆防盗器）': read_bit(bytes, body_index + 0, 2),
        '车辆非法点火': read_bit(bytes, body_index + 0, 3),
        '车辆非法位移': read_bit(bytes, body_index + 0, 4),
        '碰撞侧翻报警': read_bit(bytes, body_index + 0, 5),

        '状态': Covert.bytes_2_hex_string(bytes, body_index + 4, 4),
        'ACC': read_bit(bytes, body_index + 7, 0),
        '未定位/定位': read_bit(bytes, body_index + 7, 1),
        '南纬/北纬': read_bit(bytes, body_index + 7, 2),
        '东经/西京': read_bit(bytes, body_index + 7, 3),
        '运营状态/停运状态': read_bit(bytes, body_index + 7, 4),
        '经纬度加密': read_bit(bytes, body_index + 7, 5),
        '油路状态': read_bit(bytes, body_index + 6, 2),
        '电路状态': read_bit(bytes, body_index + 6, 3),
        '车迷加锁': read_bit(bytes, body_index + 6, 4),
        '纬度': Covert.bytes_2_hex_string(bytes, body_index + 8, 4),
        '经度': Covert.bytes_2_hex_string(bytes, body_index + 12, 4),
        '高程': Covert.bytes_2_hex_string(bytes, body_index + 16, 2),
        '速度': Covert.bytes_2_hex_string(bytes, body_index + 18, 2),
        '方向': Covert.bytes_2_hex_string(bytes, body_index + 20, 2),
        '时间': Covert.bytes_2_hex_string(bytes, body_index + 22, 6) + '[' + format_timestamp(int(Covert.bytes_2_hex_string(bytes, body_index + 22, 6))) + ']',
    }}

def decode_0x8103(bytes):
    body_index = get_message_body_index(bytes)
    body_length = get_message_body_length(bytes)
    return {**decode_header(bytes), **{
    # return {**{
        '含义': '设置终端参数',
        '消息体': Covert.bytes_2_hex_string(bytes, body_index, body_length),
        '参数总数': Covert.bytes_2_number(bytes, body_index + 0, 1),
    }, **decode_0x8103_params(bytes, body_index + 1, body_length - 1)}

def decode_0x8103_params(bytes, src_pos, length):
    params = {}

    count = 0
    index = src_pos
    while index < src_pos + length:
        count += 1
        id = Covert.bytes_2_hex_string(bytes, index, 4)
        step = Covert.bytes_2_number(bytes, index + 4, 1)
        params['序号:{0} 参数ID:{1} 参数长度:{2}'.format(count, id, step)] = decode_8103_param(id, bytes[index + 5: index + 5 + step])

        if step == 0:
            index += 4
        else:
            index += int(step + 5)

    return {**{
        '参数列表': Covert.bytes_2_hex_string(bytes, src_pos, length),
    }, **params}

def decode_8103_param(id, bytes):
    decoders_8103_param = {
        '00000001': ('number', 4, '终端心跳发送间隔', 's'),
        '00000002': ('number', 4, 'TCP消息应答超时时间', '次'),
        '00000003': ('number', 4, 'TCP消息重传次数', '次'),
        '00000004': ('number', 4, 'UDP消息应答超时时间', '次'),
        '00000005': ('number', 4, 'UDP消息重传次数', '次'),
        '00000006': ('number', 4, 'SMS消息应答超时时间', '次'),
        '00000007': ('number', 4, 'SMS消息重传次数', '次'),
        '00000010': ('gbk', -1, '主服务器APN'),
        '00000011': ('gbk', -1, '主服务器无线通信拨号用户名'),
        '00000012': ('gbk', -1, '主服务器无线通信拨号密码'),
        '00000013': ('gbk', -1, '主服务器地址'),
        '00000014': ('gbk', -1, '备份服务器APN'),
        '00000015': ('gbk', -1, '备份服务器无线通信拨号用户名'),
        '00000016': ('gbk', -1, '备份服务器无线通信拨号密码'),
        '00000017': ('gbk', 4, '备份服务器地址'),
        '00000018': ('number', 4, '服务器TCP端口', ''),
        '00000019': ('number', 4, '服务器UDP端口', ''),
        '00000020': ('number', 4, '位置汇报策略', '（0：定时；1：定距；2：定时和定距）'),
        '00000021': ('number', 4, '位置汇报方案', '（0：根据ACC状态；1：根据登录状态和ACC状态，先判断登录状态，若登录再根据ACC状态）'),
        '00000022': ('number', 4, '驾驶员未登录汇报时间间隔', 's'),
        '00000027': ('number', 4, '休眠时汇报时间间隔', 's'),
        '00000028': ('number', 4, '紧急报警汇报时间间隔', 's'),
        '00000029': ('number', 4, '缺省时间汇报间隔', 's'),
        '0000002C': ('number', 4, '缺省距离汇报间隔', '米'),
        '0000002D': ('number', 4, '驾驶员未登录汇报距离间隔', '米'),
        '0000002E': ('number', 4, '休眠时汇报距离间隔', '米'),
        '0000002F': ('number', 4, '紧急报警汇报距离间隔', '米'),
        '00000030': ('number', 4, '挂点补传角度', '（<180)'),
        '00000040': ('gbk', -1, '监控平台电话号码'),
        '00000041': ('gbk', -1, '复位电话号码'),
        '00000042': ('gbk', -1, '恢复出厂设置电话号码'),
        '00000043': ('gbk', -1, '监控平台SM电话'),
        '00000044': ('gbk', -1, '接收终端SMS文本报警号码'),
        '00000045': ('number', 4, '终端电话接听策略', '（0：自动接听；1：ACC ON时自动接听，OFF时手动接听）'),
        '00000046': ('number', 4, '每次最长通话时间', 's（0：不允许通话；0xFFFFFFFF为不限制）'),
        '00000047': ('number', 4, '每月最长通话时间', 's（0：不允许通话；0xFFFFFFFF为不限制）'),
        '00000048': ('gbk', -1, '监听电话号码'),
        '00000049': ('gbk', -1, '监管平台特权短信号码'),
        '00000050': ('hex', -1, '报警屏蔽字'),
        '00000051': ('hex', 4, '报警发送文本SMS开关'),
        '00000052': ('hex', 4, '报警拍摄开关'),
        '00000053': ('hex', 4, '报警拍摄存储标志'),
        '00000054': ('hex', 4, '关键标志'),
        '00000055': ('number', 4, '最高速度', 'km/h'),
        '00000056': ('number', 4, '超速持续时间', 's'),
        '00000057': ('number', 4, '连续驾驶时间门限', 's'),
        '00000058': ('number', 4, '当天累计驾驶时间门限', 's'),
        '00000059': ('number', 4, '最小休息时间', 's'),
        '0000005A': ('number', 4, '最长停车时间', 's'),
        '00000070': ('number', 4, '图像质量', '（1～10，1最好）'),
        '00000071': ('number', 4, '亮度', '（0～255）'),
        '00000072': ('number', 4, '对比度', '（0～127）'),
        '00000073': ('number', 4, '饱和度', '（0～127）'),
        '00000074': ('number', 4, '色度', '（0～255）'),
        '00000080': ('number', 4, '车辆里程表读数', '(1/10km/h)'),
        '00000081': ('number', 2, '省域ID', ''),
        '00000082': ('number', 2, '市域ID', ''),
        '00000083': ('gbk', -1, '车牌号'),
        '00000084': ('license_pate_color', 1, '车牌颜色'),
    }

    def check_length(*args):
        if args[1] == -1:
            return '长度校验通过(0)'
        elif args[1] == len(bytes):
            return '长度校验通过(1)'
        else:
            return '长度校验失败，协议中定义长度:{0}, 实际长度:{1}'.format(args[1], len(bytes))

    def decode(*args):
        if args[0] == 'number':
            return '{0}:{1}{2}'.format(args[2], Covert.bytes_2_number(bytes, 0, len(bytes)), args[3])
        elif args[0] == 'hex':
            return '{0}:{1}'.format(args[2], Covert.bytes_2_hex_string(bytes, 0, len(bytes)))
        elif args[0] == 'gbk':
            return '{0}:{1}'.format(args[2], bytes.fromhex(Covert.bytes_2_hex_string(bytes, 0, len(bytes))).decode('GBK'))
        elif args[0] == 'license_pate_color':
            return '{0}:{1}'.format(args[2], str(LicensePateColor(Covert.bytes_2_number(bytes, 0, len(bytes)))).split('.')[1])
        else:
            return 'type[{0}]传递错误，请检查'.format(type)

    if id in decoders_8103_param.keys():
        return '参数值:{0} {1} {2}'.format(Covert.bytes_2_hex_string(bytes, 0, len(bytes)), check_length(*(decoders_8103_param[id])), decode(*(decoders_8103_param[id])))
    else:
        return '参数值:{0} {1}'.format(Covert.bytes_2_hex_string(bytes, 0, len(bytes)), '参数不支持解析')



decoders = {
    '0100': decode_0x0100,
    '0200': decode_0x0200,
    '8001': decode_0x8001,
    '8100': decode_0x8100,
    '8103': decode_0x8103,
}


if __name__ == '__main__':
    # x0200 = '7E0200001C065030018404000500000000000000030000000000000000000000000000190423172359AC7E'
    # print(x0200)
    # params = decode_hex_string(x0200)
    # for key, value in params.items():
    #     print(key, value)

    # # x8103 = '7E8103002B0650300184040004050000008308D5E341383838383800000082020D490000008102002200000080040000003C000000840104D77E'
    # x8103 = '7E8103001C065030018404001C0300000057040000002A00000055040000002A00000056040000002A1C7E'
    # print(x8103)
    # params = decode_hex_string(x8103)
    # for key, value in params.items():
    #     print(key, value)

    msg = '7E000200000650300184040DD9317E'
    print(decode_hex_string(msg))
    pass