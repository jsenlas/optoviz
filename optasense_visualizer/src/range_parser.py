#!/usr/bin/env python
def parse_range(range_str):
    range_start_end = range_str.split("-")
    try:
        start = int(range_start_end[0])
        end = int(range_start_end[-1])
    except ValueError as exc:
        start = 0
        end = 100

    return list(range(start, end+1))

def parse_channel_range(string):
    selected_channels = []
    for i in string.split(";"):
        if not i:
            continue
        if "-" in i:
            selected_channels.extend(parse_range(i))
        else:
            selected_channels.append(int(i))
    return sorted(set(selected_channels))

# test
# x = "17;35;128;14-23;-30;"
# print(parse_channel_range(x))