from subprocess import Popen, PIPE


def collect_file_ost_path_info(pid, src_path):
    proc = Popen(['ls', '-l', '/proc/' + str(int(pid.strip())) + '/fd/'], universal_newlines=True, stdout=PIPE)
    # total 0
    # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 0 -> /dev/pts/98
    # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 1 -> /dev/pts/98
    # lrwx------ 1 ehsansa sub102 64 Nov 22 13:48 2 -> /dev/pts/98
    # lr-x------ 1 ehsansa sub102 64 Nov 22 14:09 3 -> /home/ehsansa/sample_text.txt
    res = proc.communicate()[0]

    #print (res)
    res_parts = res.split("\n")
    for line in res_parts:
        if len(line.strip()) > 0:
            if src_path in line:
                slash_index = line.rfind(">")
                file_name = line[slash_index + 1:].strip()
                
                first_slash_index = file_name.find("/")
                second_slash_index = file_name.find("/", first_slash_index + 1)
                file_mount_point = file_name[first_slash_index + 1: first_slash_index + second_slash_index]

                proc = Popen(['lfs', 'getstripe', file_name], universal_newlines=True, stdout=PIPE)
                # /expanse/lustre/scratch/ehsansa/temp_project/sample_text.txt
                # lmm_stripe_count:  1
                # lmm_stripe_size:   1048576
                # lmm_pattern:       raid0
                # lmm_layout_gen:    0
                # lmm_stripe_offset: 61
                #	obdidx		 objid		 objid		 group
                #	    61	      10861858	     0xa5bd22	   0xac0000400
                #
                res1 = proc.communicate()[0]

                res_parts1 = res1.split("\n")
                for x in range(len(res_parts1)):
                    if "obdidx" in res_parts1[x] or "l_ost_idx" in res_parts1[x]:
                        ost_number = 0
                        if "obdidx" in res_parts1[x]:
                            parts = res_parts1[x + 1].strip().split("\t")
                            # print(parts)
                            # print(parts[0])
                            ost_number = int(parts[0].strip())
                            #print(ost_number)
                        else:
                            parts = res_parts1[x].strip().split("l_ost_idx: ")[1].split(",")
                            ost_number = int(parts[0].strip())
                        # Convert obdidx or l_ost_idx from 10 base into hex
                        # hex_ost_number = hex(int(ost_number))
                        # x_insex = hex_ost_number.rfind("x")
                        # hex_ost_number = hex_ost_number[x_insex + 1:]
                        hex_ost_number = '{0:0{1}X}'.format(int(ost_number), 4)
                        proc = Popen(['ls', '-l', '/sys/kernel/debug/lustre/osc'], universal_newlines=True, stdout=PIPE)
                        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0045-osc-ffff92b94ed33000
                        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0046-osc-ffff92b900cb0000
                        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0046-osc-ffff92b94ed33000
                        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0047-osc-ffff92b900cb0000
                        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0047-osc-ffff92b94ed33000
                        res = proc.communicate()[0]
                        parts = res.split("\n")
                        ost_str = "-OST" + hex_ost_number
                        
                        for x in range(1, len(parts)):
                            ost_name_parts = parts[x].split(" ")
                            for part in ost_name_parts:
                                #print (part, file_mount_point, ost_str)
                                #if file_mount_point in part and ost_str in part and "OST" in part:
                                first_dash_index = part.find("-")                               
                                if first_dash_index != -1 and part[0:first_dash_index] in file_mount_point and ost_str in part and "OST" in part:
                                    first_dash_index = part.find("-")
                                    second_dash_index = part.find("-", first_dash_index + 1)

                                    first_part = part[:first_dash_index]
                                    second_part = part[second_dash_index + 1:]

                                    # ost_str = "-OST" + hex_ost_number
                                    ost_dir_name = first_part + ost_str + "-"  + second_part
                                    ost_path = '/proc/fs/lustre/osc/' + ost_dir_name

                                    # print(ost_path)
                                    return ost_path, ost_dir_name
                        break
