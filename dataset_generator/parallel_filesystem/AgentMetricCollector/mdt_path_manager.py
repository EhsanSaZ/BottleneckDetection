from subprocess import Popen, PIPE
import re

class OSTPathManager:
    def update_mdt_path_info(self, mdt_path_dict):
        re_pattern = r"(?P<info_part>.* )(?P<mdt_dir_name>(?P<lustre_name>.*)(?P<mdt_str>-MDT\d\d\d\d)-.*)"
        proc = Popen(['ls', '-l', '/sys/kernel/debug/lustre/mdc/'], universal_newlines=True, stdout=PIPE)
        # drwxr-xr-x 2 root root 0 Jan 18 15:41 lustre-MDT0000-mdc-ffff8ec77790f800
        res = proc.communicate()[0]
        parts = res.split("\n")
        for i in range(1, len(parts)):
            match = re.search(re_pattern, parts[i])
            if match:
                gp_dict = match.groupdict()
                match_mdt_dir_name = gp_dict.get("mdt_dir_name") or ""
                match_lustre_name = gp_dict.get("lustre_name") or ""
                match_mdt_str = gp_dict.get("mdt_str") or ""

                key = match_mdt_str if match_mdt_str != "" else "unknown"
                info_dict = {"mdt_dir_name": match_mdt_dir_name,
                             "lustre_name": match_lustre_name,
                             "mdt_str": match_mdt_str}
                if mdt_path_dict.get(key) == None:
                    mdt_path_dict[key] = [info_dict]
                else:
                    mdt_info_list = mdt_path_dict.get(key)
                    mdt_info_list.append(info_dict)
                    mdt_path_dict[key] = mdt_info_list

