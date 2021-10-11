from subprocess import Popen, PIPE


def get_buffer_value():
    value_list = []

    proc = Popen(['cat', '/proc/sys/net/ipv4/tcp_rmem'], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\t")
    for line in res_parts:
        if len(line.strip()) > 0:
            value = int(line.strip())
            value_list.append(value)

    proc = Popen(['cat', '/proc/sys/net/ipv4/tcp_wmem'], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\t")
    for line in res_parts:
        if len(line.strip()) > 0:
            value = int(line.strip())
            value_list.append(value)

    return value_list
