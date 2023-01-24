import binascii


def hex_string_to_hex_data(hex_string):
    # convert the hex string to bytes
    hex_bytes = binascii.unhexlify(hex_string)
    return hex_bytes

def find_bytes(filename, byte_string):
    with open(filename, 'rb') as f:
        data = f.read()
    offset = 0
    offsets = []
    while True:
        offset = data.find(byte_string, offset)
        if offset == -1:
            break
        offsets.append(offset)
        offset += len(byte_string)
    if not offsets:
        print("Byte String not located in the file.")
    return offsets

def print_offsets_hex(offsets):
    for offset in offsets:
        print(f"0x{offset:x}")


filepath = input("Input filepath:\n> ")
if filepath == "":
    filepath = "/home/joshcampbell/B9727AM2.20230104.215121"
bytes_to_seek = input("Input hex representation of bytes to look for:\n> ")
if bytes_to_seek == "":
    #bytes_to_seek = "C1D5F0C2"
    bytes_to_seek = "C1D5F0"
print("filepath: <%s>" % filepath)
bytes_to_seek = hex_string_to_hex_data(bytes_to_seek) 
print(bytes_to_seek)
offsets = find_bytes(filepath, bytes_to_seek)
print("Founds %s offsets" % len(offsets))
print(offsets)
print_offsets_hex(offsets)