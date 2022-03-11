import struct
from matplotlib import pyplot as plt

import serial

test_serial = serial.Serial("COM3", baudrate=115200, timeout=1)

get_module_temp_cmd = 0x01
get_module_PN_cmd = 0x03
get_module_SN_cmd = 0x04
get_module_pixel_length_cmd = 0x0A
set_module_TEC_temp_cmd = [0x12, 0x06]
get_module_TEC_temp_cmd = 0x13
get_module_optics_temp_cmd = 0x35
get_module_board_temp_cmd = 0x36
set_module_integral_time_cmd = [0x14, 0x06]
get_module_integral_time_cmd = 0x41
get_module_integral_time_max_cmd = 0x42
get_module_integral_time_min_cmd = 0x43
get_module_dark_current_cmd = 0x23
get_module_dark_current_sync_cmd = [0x2F, 0x06]
start_CCD_scan_cmd = 0x16
read_CCD_scan_cmd = 0x17
set_module_acquisition_average_cmd = [0x28, 0x06]
start_CCD_scan_sync_cmd = [0x1E, 0x06]
start_external_trigger_cmd = [0x1F, 0x06]
get_module_wavelength_calibration_coefficient_cmd = [0x55, 0x06, 0x00, 0x01]
set_lamp_cmd = [0x60, 0x05]
set_gpio_cmd = [0x61, 0x06]
set_xenon_level_cmd = [0x2D, 0x05]


def write_cmd_with_data(cmd, length, data):
    sum = 0
    package = bytearray()
    package.append(0xAA)
    package.append(0x55)
    package.append(0x00)
    package.append(length)
    package.append(cmd)
    for i in range(length - 4):
        package.append(data[i])
        sum += data[i]
    sum += cmd + length
    package.append(sum & 0xFF)
    test_serial.write(package)


def write_no_data(cmd):
    package = bytearray()
    package.append(0xAA)
    package.append(0x55)
    package.append(0x00)
    package.append(0x04)
    package.append(cmd)
    package.append(4 + cmd)
    test_serial.write(package)


def read_data():
    data = test_serial.readall()
    hex_list = [data.hex()[i:i + 2] for i in range(0, len(data.hex()), 2)]
    print(hex_list)
    return hex_list


def checksum(data, data_length):
    check_sum = 0
    for i in range(data_length + 3):
        check_sum += int(data[i + 2], 16)
    check_sum = check_sum & 0xFF
    if check_sum == int(data[len(data) - 1], 16):
        return True
    else:
        return False


def get_module_temp():
    write_no_data(get_module_temp_cmd)
    data = read_data()
    if not checksum(data, 5):
        print("checksum error")
        return -1
    temp_data = ''
    for i in range(5):
        temp_data += data[i + 5]
    return float(bytearray.fromhex(temp_data).decode())


def get_module_pn():
    write_no_data(get_module_PN_cmd)
    data = read_data()
    if not checksum(data, 11):
        print("checksum error")
        return -1
    pn_data = ''
    for i in range(11):
        pn_data += data[i + 5]
    return bytearray.fromhex(pn_data).decode()


def get_module_sn():
    write_no_data(get_module_SN_cmd)
    data = read_data()
    if checksum(data, 8):
        print("checksum error")
        return -1
    sn_data = ''
    for i in range(11):
        sn_data += data[i + 5]
    return bytearray.fromhex(sn_data).decode()


def get_module_pixel_length():
    write_no_data(get_module_pixel_length_cmd)
    data = read_data()
    if checksum(data, 2):
        print("checksum error")
        return -1
    return int(data[len(data) - 2], 16)


def get_tec_temp():
    write_no_data(get_module_TEC_temp_cmd)
    data = read_data()
    if checksum(data, 5):
        print("checksum error")
        return -1
    temp_data = ''
    for i in range(5):
        temp_data += data[i + 5]
    return float(bytearray.fromhex(temp_data).decode())


# def get_optics_temp():
#     write_no_data(get_module_optics_temp_cmd)
#     data = read_data()
#     if checksum(data, 5):
#         print("checksum error")
#         return -1
#     temp_data = ''
#     for i in range(5):
#         temp_data += data[i + 5]
#     return float(bytearray.fromhex(temp_data).decode())
#
#
# def get_board_temp():
#     write_no_data(get_module_board_temp_cmd)
#     data = read_data()
#     if checksum(data, 5):
#         print("checksum error")
#         return -1
#     temp_data = ''
#     for i in range(5):
#         temp_data += data[i + 5]
#     return float(bytearray.fromhex(temp_data).decode())


def get_module_integral_time():
    write_no_data(get_module_integral_time_cmd)
    data = read_data()
    if checksum(data, 2):
        print("checksum error")
        return -1
    integral_time_data = ''
    for i in range(2):
        integral_time_data += data[i + 5]
    return int(integral_time_data, 16)


def get_ccd():
    write_no_data(read_CCD_scan_cmd)
    data = read_data()
    if data[5] == 'FF':
        return -1
    if not checksum(data, 4097):
        print("checksum error")
        return -1
    ccd_data = ''
    for i in range(4096):
        ccd_data += data[i + 6]
    hex_data = [int(ccd_data[i:i + 4], 16) - 3300 if int(ccd_data[i:i + 4], 16) > 3300 else 0 for i in
                range(0, len(ccd_data), 4)]
    return hex_data


def get_wavelength_calibration():
    write_cmd_with_data(get_module_wavelength_calibration_coefficient_cmd[0],
                        get_module_wavelength_calibration_coefficient_cmd[1],
                        [get_module_wavelength_calibration_coefficient_cmd[2],
                         get_module_wavelength_calibration_coefficient_cmd[3]])
    data = read_data()
    if not checksum(data, 32):
        print("checksum error")
        return -1
    wavelength_calibration_data = ''
    for i in range(16):
        wavelength_calibration_data += data[i + 21]
    wave_list = [wavelength_calibration_data[i:i + 8] for i in range(0, len(wavelength_calibration_data), 8)]
    print(wave_list)
    num_list = []
    for i in range(4):
        num_list.append(struct.unpack('<f', bytes.fromhex(wave_list[i]))[0])
    return num_list


def table():
    coneff = get_wavelength_calibration()
    tables = []
    for i in range(2048):
        temp = coneff[0] * pow(i, 3) + coneff[1] * pow(i, 2) + coneff[2] * i + coneff[3]
        tables.append(temp)
    return tables


def get_dark_current():
    write_no_data(get_module_dark_current_cmd)
    data = read_data()


def start_scan():
    write_no_data(start_CCD_scan_cmd)
    data = read_data()


def get_wave_length():
    start_scan()
    get_dark_current()
    ccd_data = get_ccd()
    tables = table()
    plt.plot(tables, ccd_data, 'g^')
    plt.show()
