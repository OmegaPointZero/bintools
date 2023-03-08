import time

class BinaryFileReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.EBCDIC_CHARS = {
            "90": "!",
            "91": "$",
            "92": "*",
            "93": ")",
            "94": ";",
            "95": "¬",
            "96": "-",
            "97": "/",
            "106": "¦",
            "107": ",",
            "108": "%",
            "109": "_",
            "110": ">",
            "111": "?",
            "121": "`",
            "122": ":",
            "123": "#",
            "124": "@",
            "125": "'",
            "126": "=",
            "127": "\"",
            "129": "a",
            "130": "b",
            "131": "c",
            "132": "d",
            "133": "e",
            "134": "f",
            "135": "g",
            "136": "h",
            "138": "i",
            "145": "j",
            "146": "k",
            "147": "l",
            "148": "m",
            "149": "n",
            "150": "o",
            "151": "p",
            "152": "q",
            "153": "r",
            "161": "~",
            "162": "s",
            "163": "t",
            "164": "u",
            "165": "v",
            "166": "w",
            "167": "x",
            "168": "y",
            "169": "z",
            "192": "{",
            "193": "A",
            "194": "B",
            "195": "C",
            "196": "D",
            "197": "E",
            "198": "F",
            "199": "G",
            "200": "H",
            "202": "I",
            "208": "}",
            "209": "J",
            "210": "K",
            "211": "L",
            "212": "M",
            "213": "N",
            "214": "O",
            "215": "P",
            "216": "Q",
            "217": "R",
            "226": "S",
            "227": "T",
            "228": "U",
            "229": "V",
            "230": "W",
            "231": "X",
            "232": "Y",
            "233": "Z",
            "240": "0",
            "241": "1",
            "242": "2",
            "243": "3",
            "244": "4",
            "245": "5",
            "246": "6",
            "247": "7",
            "248": "8",
            "249": "9"
        }


    def read_file(self):
        start_time = time.time()
        print(f"Start time: {time.ctime(start_time)}")
        with open(self.file_path, 'rb') as f:
            self.data = f.read()
        end_time = time.time()
        print(f"End time: {time.ctime(end_time)}")
        print(f"Time taken to load file: {end_time - start_time} seconds")

    def print_hex_bytes(self, data, 
        start_address=0, end_address=None, bytes_per_line=16, encoding='ASCII'):
        if end_address is None:
            end_address = len(data)
        if start_address >= end_address:
            raise ValueError("Start address should be less than end address")
        if end_address > len(data):
            end_address = len(data)
        offset = start_address
        while offset < end_address:
            line = data[offset:offset+bytes_per_line]
            hex_offset = f"{offset:08x}"
            hex_line = " ".join(f"{b:02x}" for b in line)
            if encoding == 'ASCII':
                ascii_line = "".join(chr(b) if 32 <= b <= 126 else '.' for b in line)
                print(f"{hex_offset}  {hex_line} |{ascii_line}|")
            else:
                print(f"{hex_offset}  {hex_line}")
            offset += bytes_per_line

    def render_text_output_line(self, hex_offset, hex_line, encoding):
        if encoding == 'ASCII':
            ascii_line = "".join(chr(int(b,16)) if 32 <= int(b,16) <= 126 else '.' for b in hex_line.split())
            line = f"[ 0x{hex_offset} ]: {hex_line}    |{ascii_line}|"
            return line
        elif encoding == 'EBCDIC':
            ebcdic_line = "".join(self.EBCDIC_Lookup(str(int(byte,16))) for byte in hex_line.split())
            line = f"[ 0x{hex_offset} ]: {hex_line}    |{ebcdic_line}|"
            return line
        else:
            line = f"`[ 0x{hex_offset} ]: {hex_line}"
            return line

    def EBCDIC_Lookup(self, character):
        if character in self.EBCDIC_CHARS:
            return self.EBCDIC_CHARS[character]
        else:
            return "."

    def render_hex_bytes_loop(self, data, start_address=0, end_address=None, bytes_per_line=16, encoding='ASCII'):
        try:
            while True:
                if end_address is None:
                    end_address = len(data)
                offset = start_address
                while offset < end_address:
                    line = data[offset:offset+bytes_per_line]
                    hex_offset = f"{offset:08x}"
                    hex_line = " ".join(f"{b:02x}" for b in line)
                    print(self.render_text_output_line(hex_offset, hex_line, encoding))
                    offset += bytes_per_line
                comma_separated_range = input("Input the hex strings for <start, end>:\n> ").replace(" ", "").split(",")
                start_address = comma_separated_range[0]
                end_address = comma_separated_range[1]
                if start_address == "":
                    start_address = 0
                else:
                    start_address = int(start_address, 16)
                if end_address == "":
                    end_address = None
                else:
                    end_address = int(end_address, 16)
        except KeyboardInterrupt:
            print("Exiting program")

    def render_hex_bytes(self, data, start_address=0, end_address=None, bytes_per_line=16, encoding='ASCII'):
        if end_address is None:
            end_address = len(data)
        offset = start_address
        hex_and_text = ""
        while offset < end_address:
            line = data[offset:offset + bytes_per_line]
            hex_offset = f"{offset:08x}"
            hex_line = " ".join(f"{b:02x}" for b in line)
            hex_and_text += self.render_text_output_line(hex_offset, hex_line, encoding) + "\n"
            offset += bytes_per_line
        return hex_and_text


if __name__ == "__main__":
    filepath = input("Input filepath:\n> ")
    if filepath == "":
        filepath = "/Users/joshuacampbell/Documents/missionLane/B9727AM9.20230108.205055"
    reader = BinaryFileReader(filepath)
    reader.read_file()
    reader.render_hex_bytes_loop(reader.data, end_address=0x100, bytes_per_line=32, encoding="EBCDIC")
