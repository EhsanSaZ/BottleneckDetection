import requests


class RemoteLustreOstStatCollector:
    def process_remote_lustre_ost_stats(self, ost_agent_address, remote_ost_dir_name, remote_ost_stats_so_far=None):
        path = "obdfilter." + remote_ost_dir_name + ".stats"
        r = requests.post(ost_agent_address + "lctl_get_param", json={"path": path})
        # print(r.json()["out_put"])
        output = r.json()["out_put"] or ""
        value_list = []
        if remote_ost_stats_so_far is None:
            ost_stat_so_far = {}
        output_parts = output.split("\n")
        remote_ost_stats_latest_value = {}
        for metric_line in output_parts:
            if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line and not remote_ost_dir_name in metric_line:
                tokens = str(metric_line).split(" ")
                if tokens[0] == "read_bytes" or tokens[0] == "write_bytes":
                    remote_ost_stats_latest_value[tokens[0]] = float(tokens[len(tokens) - 1])

        value_list.append(float(
            (remote_ost_stats_latest_value.get("read_bytes") or 0) - (remote_ost_stats_so_far.get("read_bytes") or 0)))
        value_list.append(float((remote_ost_stats_latest_value.get("write_bytes") or 0) - (
                remote_ost_stats_so_far.get("write_bytes") or 0)))
        return value_list, remote_ost_stats_latest_value
