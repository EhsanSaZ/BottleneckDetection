import re
from subprocess import Popen, PIPE


class OSTPathManager:
    def update_ost_path_info(self, ost_path_dict):
        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0047-osc-ffff92b94ed33000
        re_pattern = r"(?P<info_part>.* )(?P<ost_dir_name>(?P<remote_ost_dir_name>(?P<lustre_name>.*)(?P<ost_str>-OST\d\d\d\d))-.*)"

        proc = Popen(['ls', '-l', '/sys/kernel/debug/lustre/osc'], universal_newlines=True,
                     stdout=PIPE)
        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0045-osc-ffff92b94ed33000
        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0046-osc-ffff92b900cb0000
        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0046-osc-ffff92b94ed33000
        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0047-osc-ffff92b900cb0000
        # dr-xr-xr-x 2 root root 0 Nov 22 14:14 expanse-OST0047-osc-ffff92b94ed33000
        res = proc.communicate()[0]
        parts = res.split("\n")
        for i in range(1, len(parts)):
            match = re.search(re_pattern, parts[i])
            if match:
                gp_dict = match.groupdict()
                match_ost_dir_name = gp_dict.get("ost_dir_name") or ""
                match_remote_ost_dir_name = gp_dict.get("remote_ost_dir_name") or ""
                match_lustre_name = gp_dict.get("lustre_name") or ""
                match_ost_str = gp_dict.get("ost_str") or ""

                key = match_ost_str if match_ost_str != "" else "unknown"
                info_dict = {"ost_dir_name": match_ost_dir_name,
                             "remote_ost_dir_name":match_remote_ost_dir_name,
                             "lustre_name": match_lustre_name}
                if ost_path_dict.get(key) == None:
                    ost_path_dict[key] = [info_dict]
                else:
                    ost_info_list = ost_path_dict.get(key)
                    ost_info_list.append(info_dict)
                    ost_path_dict[key] = ost_info_list
