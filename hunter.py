import paramiko
import os
import re
from colors import colors
from hexwalker import BinaryFileReader


def lookup_color(index):
    if (1 <= index <= 12) or (index == 59):
        return colors.fg.red
    elif (13 <= index <= 16) or (60 <= index <= 95):
        return colors.fg.orange
    elif (17 <= index <= 20) or (96 <= index <= 99):
        if 96 <= index <= 99:
            return colors.bg.purple + colors.fg.yellow
        return colors.fg.lightred
    elif (21 <= index <= 28) or (100 <= index <= 103):
        if 100 <= index <= 103:
            return colors.bg.purple + colors.fg.yellow
        return colors.fg.yellow
    elif (29 <= index <= 36) or (104 <= index <= 105):
        return colors.fg.pink
    elif (37 <= index <= 48) or (106 <= index <= 137):
        return colors.fg.blue
    elif (49 <= index <= 52) or (138 <= index <= 139):
        return colors.fg.cyan
    elif 53 <= index <= 54:
        return colors.fg.purple
    elif 55 <= index <= 56: # Target section, highlight it
        return colors.bg.orange + colors.fg.blue
    elif 57 <= index <= 58:
        return colors.fg.lightcyan
    return colors.reset


class Hunter:
    def __init__(self, file="./inputs/B9727AM2.20230227.211330"):
        self.file = file
        self.bytes_to_find = b'\xc1\xd4\xf0\xc2'
        self.BFR = BinaryFileReader(self.file)
        self.BFR.read_file()

    def set_bytes(self, _bytes):
        self.bytes_to_find = _bytes

    def get_bytes(self):
        return self.bytes_to_find

    def set_file(self, new_file):
        self.file = new_file

    def get_file(self):
        return self.file

    def get_initial_offsets(self):
        with open(self.file, 'rb') as f:
            data = f.read()
            self.offsets = [offset - 12 for offset in [m.start() for m in re.finditer(self.bytes_to_find, data)]]

    def process_file(self):
        # Open the file in binary mode
        with open(self.file, 'rb') as f:
            # Create a list to store the new offsets
            new_offset_list = []
            # Loop through the offsets in the input list
            for offset in self.offsets:
                # Seek to the offset + 55 bytes to get to the start of the detail record
                f.seek(offset + 55)
                # Read the next 2 bytes, which should be the Pic Clause 9(2) in Cobol EBCDIC
                _bytes = f.read(2)
                # Check the 2nd byte to see if it is equal to 21
                if _bytes[1] == 21:
                    # If it is, add the offset to the new list
                    new_offset_list.append(offset)
            # Return the new list
            return new_offset_list

    def print_target_offsets(self, start, end, bpl=32, _print=True):
        output = self.BFR.render_hex_bytes(  self.BFR.data,
                                    start_address=int(start, 16), 
                                    end_address=int(end, 16), 
                                    bytes_per_line=bpl, 
                                    encoding="EBCDIC"
                                 )
        if _print:
            print(output)
        return output

    def extract_record_details(self, record):
        bytes = []
        # Enter the bytes
        split_by_lines = record.split("\n")
        split_by_lines.remove("")
        for line in split_by_lines:
            first_split = line.split(":")
            # offset = first_split[0]
            line_after_offset = first_split[1]
            hex_bytes_string = line_after_offset.split("|")[0]
            # Strip leading/trailing spaces
            hex_bytes_string = hex_bytes_string[1:-4]
            hex_bytes = [b for b in hex_bytes_string.split(" ")]
            bytes += hex_bytes

        header = bytes[:36]
        detail = bytes[36:]
        header_account_id = header[0:12]
        header_record_type = header[12:16]
        client_number = header[16:20]
        header_xmit_id = header[20:28]
        file_creation_date = header[28:36]

        account_id = detail[:12]
        record_type = detail[12:16]
        segment_length = detail[16:18]

        acct_misc_data_type = detail[18:20]
        segment_sequence = detail[20:22]
        acct_misc_data = detail[22:]

        ebpp_enrolmnt_id = detail[22:23]
        ebpp_vendor_customer_id = detail[23:59]
        ebpp_enrolmnt_date = detail[59:63]
        ebpp_last_maint_date = detail[63:67]
        ebpp_hc_stmt_counter = detail[67:69]
        ebpp_vendor_customer_id2 = detail[69:101]
        ebpp_bounce_email_ctr = detail[101:103]

        obj = {
            "header": {
                "header_account_id": header_account_id,
                "record_type": header_record_type,
                "client_number": client_number,
                "header_transmit_id": header_xmit_id,
                "file_creation_date": file_creation_date
            },
            "detail": {
                "account_id": account_id,
                "record_type": record_type,
                "segment_length": segment_length,
                "acct_misc_data_type": acct_misc_data_type,
                "segment_sequence": segment_sequence,
                "acct_misc_data": acct_misc_data
            },
            "account_misc_data": {
                "ebpp_enrolmnt_id": ebpp_enrolmnt_id,
                "ebpp_vendor_customer_id": ebpp_vendor_customer_id,
                "ebpp_enrolmnt_date":ebpp_enrolmnt_date,
                "ebpp_last_maint_date": ebpp_last_maint_date,
                "ebpp_hc_stmt_counter": ebpp_hc_stmt_counter,
                "ebpp_vendor_customer_id2": ebpp_vendor_customer_id2,
                "ebpp_bounce_email_ctr": ebpp_bounce_email_ctr
            }
        }

        return obj

    def print_record_details(self, record_string):
        record = self.extract_record_details(record_string)
        print("HEADER" + colors.reset)
        print(colors.fg.red + "Header Account ID: "+ str(record['header']['header_account_id']) + colors.reset)
        print(colors.fg.orange +"Record Type: " + str(record['header']['record_type']) + colors.reset)
        print(colors.fg.lightred + "Client Number: " + str(record['header']['client_number']) + colors.reset)
        print(colors.fg.yellow + "Header Transmit ID: " + str(record['header']['header_transmit_id']) + colors.reset)
        print(colors.fg.pink + "File Creation Date: " + str(record['header']['file_creation_date']) + colors.reset)
        print("DETAIL RECORD" + colors.reset)
        print(colors.fg.blue + "Account ID: " + str(record['detail']['account_id']) + colors.reset)
        print(colors.fg.cyan + "Record Type: " + str(record['detail']['record_type']) + colors.reset)
        print(colors.fg.purple + "Segment Length: " + str(record['detail']['segment_length']) + colors.reset)
        print(colors.bg.orange + colors.fg.blue  + "Account Misc Data Type (Our Target, should be 21): " + str(record['detail']['acct_misc_data_type']) + colors.reset)
        print(colors.fg.lightcyan + "Segment Sequence: " + str(record['detail']['segment_sequence']) + colors.reset)
        print("So far, I have yet to see a 21 anywhere defining the AM0BU type. So, the following "
              "will be parsed to show what the data would be read as, if it IS AM0BU.")
        # print("Account Misc Data: " + colors.fg.lightred +  str(record['detail']['acct_misc_data']) + colors.reset)
        print(colors.fg.red + "EBPP Enrollment ID: " + str(record['account_misc_data']['ebpp_enrolmnt_id']) + colors.reset)
        print(colors.fg.orange + "EBPP Customer ID: " + str(record['account_misc_data']['ebpp_vendor_customer_id']) + colors.reset)
        print(colors.bg.purple + colors.fg.yellow + "EBPP Enrollment Date: " + str(record['account_misc_data']['ebpp_enrolmnt_date']) + colors.reset)
        print(colors.bg.purple + colors.fg.yellow + "EBPP Last Maint Date: " + str(record['account_misc_data']['ebpp_last_maint_date']) + colors.reset)
        print(colors.fg.pink + "EBPP HC STMT Counter: " + str(record['account_misc_data']['ebpp_hc_stmt_counter']) + colors.reset)
        print(colors.fg.blue + "EBPP Vendor Customer ID 2: " + str(record['account_misc_data']['ebpp_vendor_customer_id2']) + colors.reset)
        print(colors.fg.cyan + "EBPP Bounce Email Counter: " + str(record['account_misc_data']['ebpp_bounce_email_ctr']) + colors.reset)

    def colorize_target_offsets(self, string):
        counted_bytes = 0
        input_lines = string.split("\n")
        input_lines.remove("")
        colored_lines = []
        for line in input_lines:
            split_line = line.split(":")
            end_split = split_line[1].split("|")
            split_line[1] = end_split[0]
            split_line.append(end_split[1])
            offset = split_line[0] + ":"
            bytes_string = split_line[1][1:-4]
            bytes_arr = bytes_string.split(" ")
            decoded_arr = list(split_line[2])
            colored_bytes_arr = []
            colored_string_arr = []
            while bytes_arr and decoded_arr:
                target_byte = bytes_arr.pop(0)
                target_char = decoded_arr.pop(0)
                counted_bytes += 1
                target_color = lookup_color(counted_bytes)
                new_byte = target_color + target_byte + colors.reset
                new_char = target_color + target_char + colors.reset
                colored_bytes_arr.append(new_byte)
                colored_string_arr.append(new_char)
            colored_bytes_string = " " + ' '.join(colored_bytes_arr) + "    "
            colored_string_string = "|" + ''.join(colored_string_arr) + "|"
            colored_line = offset + colored_bytes_string + colored_string_string
            colored_lines.append(colored_line)
        return "\n".join(colored_lines)


if __name__ == "__main__":
    target = "../B9727AM2.20230203.212120"
    print("Filename: %s" % target)
    hunter = Hunter(file=target)
    hunter.get_initial_offsets()
    sample_offsets = hunter.offsets
    found_values = []
    count = 0
    if len(sample_offsets) == 0:
        raise Exception("AM0B record not found in this file.")
    for offset in sample_offsets:
        count += 1
        if count % 10000 == 0:
            print("Processed %i of %i records" % (count, len(sample_offsets)))
        start = str(hex(offset))[2:]
        end = str(hex(offset + 200))[2:]
        parsed_offset_string = hunter.print_target_offsets(start, end, _print=False)
        details = hunter.extract_record_details(parsed_offset_string)
        colorized = hunter.colorize_target_offsets(parsed_offset_string)
        if count in [1, 888, 77777]:
            print("COUNT: %i" % count)
            print(colorized)
            hunter.print_record_details(parsed_offset_string)
        adt = details['detail']['acct_misc_data_type']
        if adt not in found_values:
            found_values.append(adt)

# this one programmatically calls from the AWS S3- re-written above to process individual files.
"""
if __name__ == "__main__":
    # target = "./inputs/B9727AM2.20230227.211330"
    inputs_dir = "inputs/"
    target_files = open("target_output.txt", "r").read().split("\n")
    read_files = 3350
    os.makedirs("good", exist_ok=True)
    while True:
        input_files = os.listdir(inputs_dir)
        if len(input_files) == 0:
            print("Files processed so far: %s" % read_files)
            if read_files < len(target_files):
                next_file_number = read_files + 10 if len(target_files) <= read_files + 10 else len(target_files) - 1
                files_to_get = target_files[read_files:read_files+10]
                read_files += 10
                for ftg in files_to_get:
                    # Get the file.
                    command = "aws s3 cp s3://vault-production-01-audits-01-data-1mwnts0afa67h/live/vaults/tntrscbp87u/%s ./%s" % (ftg, inputs_dir)
                    os.system(command)
                input_files = os.listdir(inputs_dir)
        try:
            target = input_files[0]
            print("Filename: %s" % target)
            hunter = Hunter(file=inputs_dir + target)
            hunter.get_initial_offsets()
            sample_offsets = hunter.offsets
            found_values = []
            count = 0
            if len(sample_offsets) == 0:
                raise Exception("AM0B record not found in this file.")
            for offset in sample_offsets:
                count += 1
                if count % 10000 == 0:
                    print("Processed %i of %i records" % (count, len(sample_offsets)))
                start = str(hex(offset))[2:]
                end = str(hex(offset + 200))[2:]
                parsed_offset_string = hunter.print_target_offsets(start, end, _print=False)
                details = hunter.extract_record_details(parsed_offset_string)
                colorized = hunter.colorize_target_offsets(parsed_offset_string)
                if count in [1, 888, 77777]:
                    print("COUNT: %i" % count)
                    print(colorized)
                    hunter.print_record_details(parsed_offset_string)
                adt = details['detail']['acct_misc_data_type']
                if adt not in found_values:
                    found_values.append(adt)
            print(found_values)
            gf = open("goodfiles.txt", "a")
            gf.write(target + "\n")
            gf.close
            host = os.environ.get("SFTP_HOST")
            port = int(os.environ.get("SFTP_PORT"))
            username = os.environ.get("SFTP_USERNAME")
            password = os.environ.get("SFTP_PASSWORD")

            # Define local and remote file paths
            local_path = "goodfiles.txt"
            remote_path = "/data/mission_lane/goodfiles.txt"

            # Create SFTP client
            sftp = paramiko.SFTPClient()

            # Connect to remote server
            sftp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sftp.connect(host, port=port, username=username, password=password)

            # Upload file
            sftp.put(local_path, remote_path)

            # Close SFTP connection
            sftp.close()
            #
            # break
        except Exception as e:
            print(e)
            bf = open("badfiles.txt", "a")
            bf.write(target+"\n")
            bf.close()
            os.remove(inputs_dir+target)
"""