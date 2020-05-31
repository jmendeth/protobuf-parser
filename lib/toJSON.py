import re
import json
import sys
import binascii


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        print("Failed to create JSON")
        return False
    print("JSON created successfully")
    return True


def clean_line(line):
    line = re.sub("(\\x1b\[3)\d(m)", "", line).replace("\x1b[m", "")
    return line


bytes_chunk_flag = False


def split_line(line):
    global bytes_chunk_flag, counter
    line = line.replace("    ", "")

    if not check_int(line[0]) and line[0] == "\"" and not bytes_chunk_flag:
        line = str(packed_flag) + " <packed> = " + \
            line[1:-1].replace("\\", "\\\\")
        line = line.replace("\\\"", "\"")
        line = line.replace("\"", "\\\"")
        line = line.split(" ", maxsplit=3)
        print(line)
        return line

    if bytes_chunk_flag:
        prefix = "1 <chunk> = "
        prefix += line.split("   ")[1].split("  ", maxsplit=1)[0]
        line = prefix

    line = line.split(" ", maxsplit=3)

    if len(line) == 4 and re.search("(bytes\s\(\d*\))", line[3]):
        bytes_chunk_flag = True

    line[3] = re.sub("(group\s\(end\s)\d*(\)\smessage:)", "<message>", line[3])
    line = [x.replace("message:", "<message>") for x in line]

    return line


def get_depth(line):
    global packed_flag
    if packed_flag:
        return int((len(line) - len(line.lstrip(' '))) / 4) - 1
    return int((len(line) - len(line.lstrip(' '))) / 4)


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


counter = 0
packed_flag = False


def run(string, write_json=False, print_json=False):
    global bytes_chunk_flag, counter, packed_flag
    result = ""
    first_line_flag = True
    packed_flag = False
    last_indent = 0

    counter = 0
    count_brackets = 0
    for line in string.split("\n")[:-1]:
        line = clean_line(line)
        # print(line)

        if first_line_flag:
            first_line_flag = not first_line_flag
            result += "{\"id\":\"" + line[:-1] + "\","
        else:
            if len(line) >= 7:
                if line[-7:] == "packed:":
                    packed_flag = line.replace(
                        "    ", "").split(" ", maxsplit=3)[0]
                    continue
            if not bytes_chunk_flag and not packed_flag and (line[-1] == ':' or not check_int(
                    line.replace("    ", "")[0]) or re.search("(bytes\s\(\d*\))", line.split(" = ")[1])):
                if get_depth(line) <= last_indent - 1 and count_brackets:
                    count_brackets -= 1 * \
                        (abs(get_depth(line) - last_indent - 1) - 1)
                    result += "}" * \
                        (abs(get_depth(line) - last_indent - 1) - 2)
                    result += "},"
                s0, s1, s2, s3 = split_line(line)
                if get_depth(line) == last_indent:
                    result += ",\"" + s3 + "_" + s0 + \
                        "_" + str(counter) + "\":{"
                else:
                    result += "\"" + s3 + "_" + s0 + \
                        "_" + str(counter) + "\":{"
                counter += 1
                count_brackets += 1
                last_indent = get_depth(line)
                continue

            if get_depth(line) <= last_indent - 1 and count_brackets:
                count_brackets -= 1 * \
                    (abs(get_depth(line) - last_indent - 1) - 1)
                result += "}" * (abs(get_depth(line) - last_indent - 1) - 2)
                result += "}"
                bytes_chunk_flag = False

            s0, s1, s2, s3 = split_line(line)
            s3 = json.dumps(s3)
            if get_depth(line) == last_indent + 1:
                result += "\"" + s1 + "_" + s0 + \
                    "_" + str(counter) + "\":" + s3
            else:
                result += ",\"" + s1 + "_" + s0 + \
                    "_" + str(counter) + "\":" + s3
            counter += 1
            last_indent = get_depth(line)
            if packed_flag:
                packed_flag = False
    else:
        for x in range(count_brackets):
            result += "}"
        result += "}"

    if is_json(result):
        if print_json:
            print(result)
        if write_json:
            f = open("toJSON_result.json", "w")
            f.write(result)
            f.close()
    return result


if __name__ == '__main__':
    pass
