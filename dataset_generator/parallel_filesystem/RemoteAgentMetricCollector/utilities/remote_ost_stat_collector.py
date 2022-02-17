from subprocess import Popen, PIPE


class RemoteProcessOstStat:
    def remote_process_ost_stat(self, ost_path, ost_dir_name, ost_stat_so_far=None):
        value_list = []
        if ost_stat_so_far is None:
            ost_stat_so_far = {}

        # proc = Popen(['cat', ost_path + "/stats"], universal_newlines=True, stdout=PIPE)
        get_param_arg = "osc." + ost_dir_name + ".stats"
        proc = Popen(['lctl', 'get_param', get_param_arg], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        # snapshot_time             1637627183.394337 secs.usecs
        # req_waittime              393905757 samples [usec] 31 17820911 483362372205 28824671200467887
        # req_active                393906200 samples [reqs] 1 8243 1164349055 731470318467
        # read_bytes                299768458 samples [bytes] 0 4194304 6895163247966 -3193831078871982772
        # write_bytes               10208130 samples [bytes] 1 4194304 10917616761706 4366299781827334380
        # ost_setattr               8288718 samples [usec] 37 6862915 2072463399 268309705137179
        # ost_read                  299768458 samples [usec] 60 17820911 271513537128 5512071507059074
        # ost_write                 10208130 samples [usec] 86 15329179 98396534435 5245570501603571
        # ost_get_info              5086 samples [usec] 94 234665 2150496 74601868096
        # ost_connect               2 samples [usec] 39418 394674 434092 157321345000
        # ost_punch                 2025537 samples [usec] 44 4425929 658817331 125468513749227
        # ost_statfs                4583100 samples [usec] 34 2354832 1137583809 27790060662971
        # ost_sync                  85484 samples [usec] 35 2683564 407420351 20564344321901
        # ost_quotactl              1070893 samples [usec] 38 1131469 294654538 2901933400418
        # ldlm_cancel               31083060 samples [usec] 31 12008431 99565826195 17460575057288663
        # obd_ping                  43765 samples [usec] 52 130743 28356809 55768300189
        res_parts = res.split("\n")
        ost_stat_latest_values = {}
        for metric_line in res_parts:
            if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line and get_param_arg not in metric_line:
                tokens = str(metric_line).split(" ")
                ost_stat_latest_values[tokens[0]] = float(tokens[len(tokens) - 2])
                # value_list.append(tokens[0])
                # value = float(tokens[len(tokens) - 2])
                # value_list.append(value)

        value_list.append(
            float((ost_stat_latest_values.get("req_waittime") or 0) - (ost_stat_so_far.get("req_waittime") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("req_active") or 0) - (ost_stat_so_far.get("req_active") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("read_bytes") or 0) - (ost_stat_so_far.get("read_bytes") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("write_bytes") or 0) - (ost_stat_so_far.get("write_bytes") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("ost_setattr") or 0) - (ost_stat_so_far.get("ost_setattr") or 0)))
        value_list.append(float((ost_stat_latest_values.get("ost_read") or 0) - (ost_stat_so_far.get("ost_read") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("ost_write") or 0) - (ost_stat_so_far.get("ost_write") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("ost_get_info") or 0) - (ost_stat_so_far.get("ost_get_info") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("ost_connect") or 0) - (ost_stat_so_far.get("ost_connect") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("ost_punch") or 0) - (ost_stat_so_far.get("ost_punch") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("ost_statfs") or 0) - (ost_stat_so_far.get("ost_statfs") or 0)))
        value_list.append(float((ost_stat_latest_values.get("ost_sync") or 0) - (ost_stat_so_far.get("ost_sync") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("ost_quotactl") or 0) - (ost_stat_so_far.get("ost_quotactl") or 0)))
        value_list.append(
            float((ost_stat_latest_values.get("ldlm_cancel") or 0) - (ost_stat_so_far.get("ldlm_cancel") or 0)))
        value_list.append(float((ost_stat_latest_values.get("obd_ping") or 0) - (ost_stat_so_far.get("obd_ping") or 0)))

        # proc = Popen(['cat', ost_path + "/rpc_stats"], universal_newlines=True, stdout=PIPE)
        get_param_arg = "osc." + ost_dir_name + ".rpc_stats"
        proc = Popen(['lctl', 'get_param', get_param_arg], universal_newlines=True, stdout=PIPE)
        res = proc.communicate()[0]
        res_parts = res.split("\n")
        # snapshot_time:         1638393148.677361 (secs.usecs)
        # read RPCs in flight:  0
        # write RPCs in flight: 0
        # pending write pages:  0
        # pending read pages:   0
        for metric_line in res_parts:
            if "pending read pages" in metric_line:
                index = metric_line.find(":")
                value = float(metric_line[index + 1:])
                value_list.append(value)

            if "read RPCs in flight" in metric_line:
                index = metric_line.find(":")
                value = float(metric_line[index + 1:])
                value_list.append(value)
        return value_list, ost_stat_latest_values
