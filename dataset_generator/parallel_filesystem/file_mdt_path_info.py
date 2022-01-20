from subprocess import Popen, PIPE


def collect_file_mdt_path_info(pid, src_path):
    proc = Popen(['ls', '-l', '/proc/' + str(int(pid.strip())) + '/fd/'], universal_newlines=True, stdout=PIPE)
    # total 0
    # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 0 -> /dev/pts/98
    # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 1 -> /dev/pts/98
    # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 2 -> /dev/pts/98
    # lr-x------ 1 ehsansa sub102 64 Nov 22 14:09 3 -> /home/ehsansa/sample_text.txt
    res = proc.communicate()[0]
    res_parts = res.split("\n")
    for line in res_parts:
        if len(line.strip()) > 0:
            if src_path in line:
                slash_index = line.rfind(">")
                file_name = line[slash_index + 1:].strip()

                first_slash_index = file_name.find("/")
                second_slash_index = file_name.find("/", first_slash_index + 1)
                file_mount_point = file_name[first_slash_index + 1: first_slash_index + second_slash_index]

                proc = Popen(['lfs', 'getstripe', '-m', file_name], universal_newlines=True, stdout=PIPE)
                res1 = proc.communicate()[0]
                if res1 is not None:
                    mdt_number = int(res1)
                    hex_mdt_number = '{0:0{1}X}'.format(int(mdt_number), 4)
                    proc = Popen(['ls', '-l', '/sys/kernel/debug/lustre/mdc/'], universal_newlines=True, stdout=PIPE)
                    # drwxr-xr-x 2 root root 0 Jan 18 15:41 lustre-MDT0000-mdc-ffff8ec77790f800
                    res = proc.communicate()[0]
                    parts = res.split("\n")
                    mdt_str = "-MDT" + hex_mdt_number
                    for x in range(1, len(parts)):
                        mdt_name_parts = parts[x].split(" ")
                        for part in mdt_name_parts:
                            first_dash_index = part.find("-")
                            if first_dash_index != -1 and part[0:first_dash_index] in file_mount_point and mdt_str in part and "MDT" in part:
                                first_dash_index = part.find("-")
                                second_dash_index = part.find("-", first_dash_index + 1)

                                first_part = part[:first_dash_index]
                                second_part = part[second_dash_index + 1:]

                                mdt_path = '/sys/kernel/debug/lustre/mdc/' + first_part + mdt_str + "-" + second_part
                                return mdt_path

                else:
                    return ""
