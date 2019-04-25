import binascii


class Covert:
    @staticmethod
    def number_2_bytes(number, length):
        pass

    @staticmethod
    def bytes_2_number(bytes, src_pos, length, byteorder='big', signed=False):
        return int.from_bytes(bytes[src_pos:src_pos + length], byteorder=byteorder, signed=signed)

    # @staticmethod
    # def bytes_2_hex_string(bytes):
    #     return binascii.b2a_hex(bytes).decode('utf-8').upper()

    @staticmethod
    def bytes_2_hex_string(bytes, src_pos, length):
        return binascii.b2a_hex(bytes[src_pos:src_pos + length]).decode('utf-8').upper()

    @staticmethod
    def hex_string_2_bytes(hex_string):
        return bytes.fromhex(hex_string)

    @staticmethod
    def hex_string_2_binary_string(hex_string):
        return bin(int(hex_string, 16))[2:]

if __name__ == '__main__':
    str = '2'
    binary = Covert.hex_string_2_binary_string(str)
    print(binary)