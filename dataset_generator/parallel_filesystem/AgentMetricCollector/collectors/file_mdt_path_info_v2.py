from subprocess import Popen, PIPE
import re


class FileMdtPathInfoV2:
    def get_file_mdt_path_info(self, file_mount_point, from_string=None):
        seperator_string = '--result--'
        if from_string is not None:
            # cmd = "lfs getstripe -m {file_name}; echo {seperator}; ls -l /sys/kernel/debug/lustre/mdc/".format(file_name=file_name, seperator=seperator_string)
            # proc = Popen(['lfs', 'getstripe', '-m', file_name], universal_newlines=True, stdout=PIPE)
            # proc = Popen(cmd, shell=True, universal_newlines=True, stdout=PIPE)
            res = from_string
            res_parts_2 = res.split(seperator_string)

            # res1 = proc.communicate()[0]
            mdt_number_part = res_parts_2[0]
            if mdt_number_part is not None:
                mdt_number = int(mdt_number_part)
                hex_mdt_number = '{0:0{1}X}'.format(int(mdt_number), 4)

                # proc = Popen(['ls', '-l', '/sys/kernel/debug/lustre/mdc/'], universal_newlines=True,
                #              stdout=PIPE)
                # drwxr-xr-x 2 root root 0 Jan 18 15:41 lustre-MDT0000-mdc-ffff8ec77790f800
                # res = proc.communicate()[0]
                ls_lustre_mdc_output_parts = res_parts_2[1].split("\n")
                mdt_str = "-MDT" + hex_mdt_number
                re_pattern = r"(?P<info_part>.* )(?P<mdt_dir_name>(?P<lustre_name>.*)(?P<mdt_str>-MDT\d\d\d\d)-.*)"
                for x in range(1, len(ls_lustre_mdc_output_parts)):
                    match = re.search(re_pattern, ls_lustre_mdc_output_parts[x])
                    if match:
                        gp_dict = match.groupdict()
                        match_mdt_dir_name = gp_dict.get("mdt_dir_name") or ""
                        match_lustre_name = gp_dict.get("lustre_name") or ""
                        match_mdt_str = gp_dict.get("mdt_str") or ""
                        if match_lustre_name in file_mount_point and mdt_str == match_mdt_str and match_mdt_dir_name != "":
                            mdt_path = '/sys/kernel/debug/lustre/mdc/' + match_mdt_dir_name
                            return mdt_path, match_mdt_dir_name
                    # mdt_name_parts = parts[x].split(" ")
                    # for part in mdt_name_parts:
                    #     first_dash_index = part.find("-")
                    #     if first_dash_index != -1 and part[
                    #                                   0:first_dash_index] in file_mount_point and mdt_str in part and "MDT" in part:
                    #         first_dash_index = part.find("-")
                    #         second_dash_index = part.find("-", first_dash_index + 1)
                    #
                    #         first_part = part[:first_dash_index]
                    #         second_part = part[second_dash_index + 1:]
                    #
                    #         mdt_dir_name = first_part + mdt_str + "-" + second_part
                    #         mdt_path = '/sys/kernel/debug/lustre/mdc/' + mdt_dir_name
                    #         return mdt_path, mdt_dir_name
            # else:
            #     return ""
