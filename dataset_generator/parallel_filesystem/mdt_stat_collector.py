from subprocess import Popen, PIPE


def process_mds_rpc(mdt_path):
    proc = Popen(['cat', mdt_path + "/import"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    # import:
    # name: home-MDT0001-mdc-ffff9575076ae800
    # target: home-MDT0001_UUID
    # state: FULL
    # connect_flags: [ version, acl, inode_bit_locks, getattr_by_fid, no_oh_for_devices, max_byte_per_rpc, early_lock_cancel, adaptive_timeouts, lru_resize, fid_is_enabled, version_recovery, pools, large_ea, full20, layout_lock, 64bithash, jobstats, umask, einprogress, lvb_type, flock_deadlock, disp_stripe, open_by_fid, lfsck, multi_mod_rpcs, dir_stripe, subtree, bulk_mbits, second_flags, file_secctx, unknown2_0x200 ]
    # connect_data:
    #    flags: 0xae784e79c344d0a0
    #    instance: 66
    #    target_version: 2.12.0.4
    #    max_brw_size: 1048576
    #    ibits_known: 0x3f
    #    max_easize: 4012
    #    max_mod_rpcs: 8
    # import_flags: [ replayable, pingable, connect_tried ]
    # connection:
    #    failover_nids: [ 192.168.193.4@o2ib193, 192.168.193.3@o2ib193 ]
    #    current_connection: 192.168.193.4@o2ib193
    #    connection_attempts: 1
    #    generation: 1
    #    in-progress_invalidations: 0
    # rpcs:
    #    inflight: 0
    #    unregistering: 0
    #    timeouts: 0
    #    avg_waittime: 366 usec
    # service_estimates:
    #    services: 5 sec
    #    network: 5 sec
    # transactions:
    #    last_replay: 0
    #    peer_committed: 513097842389
    #    last_checked: 513097842389
    res_parts = res.split("\n")
    value_list = []
    for metric_line in res_parts:
        if "avg_waittime:" in metric_line:
            s_index = metric_line.find(":")
            e_index = metric_line.find("usec")
            avg_waittime = float(metric_line[s_index + 1:e_index].strip())
            value_list.append(avg_waittime)

        if "inflight:" in metric_line:
            s_index = metric_line.find(":")
            inflight = float(metric_line[s_index + 1:].strip())
            value_list.append(inflight)

        if "unregistering:" in metric_line:
            s_index = metric_line.find(":")
            unregistering = float(metric_line[s_index + 1:].strip())
            value_list.append(unregistering)

        if "timeouts:" in metric_line:
            s_index = metric_line.find(":")
            timeouts = float(metric_line[s_index + 1:].strip())
            value_list.append(timeouts)

    return value_list


def process_mdt_stat(mdt_path, mdt_stat_so_far):
    value_list = []
    if mdt_stat_so_far is None:
        mdt_stat_so_far = {}
    proc = Popen(['cat', mdt_path + "/stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    #snapshot_time             1638394164.84885 secs.usecs
    # req_waittime              1601539009 samples [usec] 26 580651352 586616437586 3987813690702099508
    # req_active                1601539009 samples [reqs] 1 15430 6031711524 7029879056572
    # mds_getattr               1935899 samples [usec] 32 123241 140181271 154613110463
    # mds_getattr_lock          58 samples [usec] 57 720 5240 1096894
    # mds_close                 267093923 samples [usec] 31 1967216 27166823734 121439574846780
    # mds_readpage              9681635 samples [usec] 123 590517 3354023669 12744165214255
    # mds_connect               1 samples [usec] 194106 194106 194106 37677139236
    # mds_statfs                4804241 samples [usec] 30 157218277 991553930 24760257751019628
    # mds_sync                  288967 samples [usec] 40 673149 1776754063 57729448137241
    # mds_quotactl              1092557 samples [usec] 41 7608664 296515154 266046508655244
    # mds_getxattr              19447242 samples [usec] 28 5162013 3087949534 155062902508702
    # ldlm_cancel               243276775 samples [usec] 27 12112838 400480363179 533988366777608771
    # obd_ping                  21790 samples [usec] 55 17192 12801137 14145734419
    # seq_query                 180 samples [usec] 42 1142 18729 4607773
    res_parts = res.split("\n")
    mdt_stat_latest_values = {}
    for metric_line in res_parts:
        if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line:
            tokens = str(metric_line).split(" ")
            mdt_stat_latest_values[tokens[0]] = float(tokens[len(tokens) - 2])
            # value_list.append(tokens[0])
            # value = float(tokens[len(tokens) - 2])
            # value_list.append(value)
    value_list.append(float((mdt_stat_latest_values.get("req_waittime") or 0) - (mdt_stat_so_far.get("req_waittime") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("req_active") or 0) - (mdt_stat_so_far.get("req_active") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_getattr") or 0) - (mdt_stat_so_far.get("mds_getattr") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_getattr_lock") or 0) - (mdt_stat_so_far.get("mds_getattr_lock") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_close") or 0) - (mdt_stat_so_far.get("mds_close") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_readpage") or 0) - (mdt_stat_so_far.get("mds_readpage") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_connect") or 0) - (mdt_stat_so_far.get("mds_connect") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_statfs") or 0) - (mdt_stat_so_far.get("mds_statfs") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_sync") or 0) - (mdt_stat_so_far.get("mds_sync") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_quotactl") or 0) - (mdt_stat_so_far.get("mds_quotactl") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("mds_getxattr") or 0) - (mdt_stat_so_far.get("mds_getxattr") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("ldlm_cancel") or 0) - (mdt_stat_so_far.get("ldlm_cancel") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("obd_ping") or 0) - (mdt_stat_so_far.get("obd_ping") or 0)))
    value_list.append(float((mdt_stat_latest_values.get("seq_query") or 0) - (mdt_stat_so_far.get("seq_query") or 0)))

    proc = Popen(['cat', mdt_path + "/md_stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    res_parts = res.split("\n")
    md_stats_so_far_dict = mdt_stat_so_far.get("md_stats") or None
    if md_stats_so_far_dict is None:
        md_stats_so_far_dict = {}
    md_stats_latest_values = {}
    #snapshot_time             1638394657.160408 secs.usecs
    # close                     267094722 samples [reqs]
    # create                    3639339 samples [reqs]
    # enqueue                   100020304 samples [reqs]
    # getattr                   1935909 samples [reqs]
    # intent_lock               2624814194 samples [reqs]
    # link                      5579059 samples [reqs]
    # rename                    2666193 samples [reqs]
    # setattr                   36255873 samples [reqs]
    # fsync                     288967 samples [reqs]
    # read_page                 45198320 samples [reqs]
    # unlink                    21058273 samples [reqs]
    # setxattr                  480869 samples [reqs]
    # getxattr                  19447312 samples [reqs]
    # revalidate_lock           425865270 samples [reqs]
    for metric_line in res_parts:
        if len(metric_line.strip()) > 0 and "snapshot_time" not in metric_line:
            tokens = str(metric_line).split(" ")
            md_stats_latest_values[tokens[0]] = float(tokens[len(tokens) - 3])
            # value_list.append(tokens[0])
            # value = float(tokens[len(tokens) - 3])
            # value_list.append(value)
    mdt_stat_latest_values["md_stats"] = md_stats_latest_values

    value_list.append(float((md_stats_latest_values.get("close") or 0) - (md_stats_so_far_dict.get("close") or 0)))
    value_list.append(float((md_stats_latest_values.get("create") or 0) - (md_stats_so_far_dict.get("create") or 0)))
    value_list.append(float((md_stats_latest_values.get("enqueue") or 0) - (md_stats_so_far_dict.get("enqueue") or 0)))
    value_list.append(float((md_stats_latest_values.get("getattr") or 0) - (md_stats_so_far_dict.get("getattr") or 0)))
    value_list.append(float((md_stats_latest_values.get("intent_lock") or 0) - (md_stats_so_far_dict.get("intent_lock") or 0)))
    value_list.append(float((md_stats_latest_values.get("") or 0) - (md_stats_so_far_dict.get("") or 0)))
    value_list.append(float((md_stats_latest_values.get("") or 0) - (md_stats_so_far_dict.get("") or 0)))

    return value_list, mdt_stat_latest_values

def get_mdt_stat(mdt_parent_path, mdt_paths, all_mdt_stat_so_far_dict):
    value_list = []
    for path in mdt_paths:
        value_list += process_mds_rpc(mdt_parent_path + path)
        a_list, mdt_stat_latest_values = process_mdt_stat(mdt_parent_path + path, all_mdt_stat_so_far_dict.get(path) or None)
        all_mdt_stat_so_far_dict[path] = mdt_stat_latest_values
        value_list += a_list
    return value_list, all_mdt_stat_so_far_dict
