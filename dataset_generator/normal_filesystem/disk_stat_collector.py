import time
from subprocess import Popen, PIPE


def get_disk_stat(drive_name, disk_io_so_far_dict=None):
    # global drive_name
    if disk_io_so_far_dict is None:
        disk_io_so_far_dict = {"sector_conversion_fctr": 2}
    proc = Popen(['cat', '/sys/block/{drive_name}/stat'.format(drive_name=drive_name)], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    time_sec = time.time()
    parts = res.split()
    parts_filtered = list(filter(None, parts))
    disk_io_latest_values = {"sector_conversion_fctr": 2, "time_so_far": time_sec,
                             "rd_ios_so_far": float(parts_filtered[0]), "rd_merges_so_far": float(parts_filtered[1]),
                             "rd_sectors_so_far": float(parts_filtered[2]), "rd_ticks_so_far": float(parts_filtered[3]),
                             "wr_ios_so_far": float(parts_filtered[4]), "wr_merges_so_far": float(parts_filtered[5]),
                             "wr_sectors_so_far": float(parts_filtered[6]), "wr_ticks_so_far": float(parts_filtered[7]),
                             "time_in_queue_so_far": float(parts_filtered[10])}
    # in_flight = float(parts_filtered[8])  # number of I/Os currently in flight
    # io_ticks = float(parts_filtered[9])  # total time this block device has been active
    # d_ios = float(parts_filtered[11])  # number of discard I/Os processed
    # d_merges = float(parts_filtered[12])  # number of discard I/Os merged with in-queue I/O
    # d_sectors = float(parts_filtered[13])  # number of sectors discarded
    # d_ticks = float(parts_filtered[14])  # total wait time for discard requests
    # fl_ios = float(parts_filtered[15])  # number of flush I/Os processed
    # fl_ticks = float(parts_filtered[16])  # total wait time for flush requests

    # proc = Popen(['iostat', '-x', drive_name], universal_newlines=True, stdout=PIPE)
    # res = proc.communicate()[0]
    # parts = res.split("\n")
    #
    # header_lst_without_space = []
    # for part in parts:
    #     if len(part.strip()) > 0 and "Device" in part:
    #         header_lst = part.split(" ")
    #         for title in header_lst:
    #             if len(title) > 0:
    #                 header_lst_without_space.append(title)
    #     elif len(part.strip()) > 0 and drive_name in part:
    #         lst = part.split(" ")
    #         lst_without_space = []
    #         lst_by_key = {}
    #         index = 0
    #         for element in lst:
    #             if len(element) > 0:
    #                 lst_without_space.append(element)
    #                 lst_by_key[header_lst_without_space[index]] = element
    #                 index += 1
    #         read_req = lst_by_key.get("r/s") or "0.0"  # lst_without_space[1]
    #         write_req = lst_by_key.get("w/s") or "0.0"  # lst_without_space[2]
    #         rkB = lst_by_key.get("rkB/s") or "0.0"  # lst_without_space[3]
    #         wkB = lst_by_key.get("wkB/s") or "0.0"  # lst_without_space[4]
    #         rrqm = lst_by_key.get("rrqm/s") or "0.0"  # lst_without_space[5]
    #         wrqm = lst_by_key.get("wrqm/s") or "0.0"  # lst_without_space[6]
    #         rrqm_perc = lst_by_key.get("%rrqm") or "0.0"  # lst_without_space[7]
    #         wrqm_perc = lst_by_key.get("%wrqm") or "0.0"  # lst_without_space[8]
    #         r_await = lst_by_key.get("r_await") or "0.0"  # lst_without_space[9]
    #         w_await = lst_by_key.get("w_await") or "0.0"  # lst_without_space[10]
    #         areq_sz = lst_by_key.get("aqu-sz") or "0.0"  # lst_without_space[11]
    #         rareq_sz = lst_by_key.get("rareq-sz") or "0.0"  # lst_without_space[12]
    #         wareq_sz = lst_by_key.get("wareq-sz") or "0.0"  # lst_without_space[13]
    #         svctm = lst_by_key.get("svctm") or "0.0"  # lst_without_space[14]
    #         util = lst_by_key.get("%util") or "0.0"  # lst_without_space[15]
    # # print(read_req," ",write_req," ",rkB," ",wkB," ",rrqm," ",wrqm," ",rrqm_perc," ",wrqm_perc," ",r_await," ",w_await," ",areq_sz," ",rareq_sz," ",wareq_sz," ",svctm," ",util)

    time_interval = disk_io_latest_values.get("time_so_far") - (disk_io_so_far_dict.get("time_so_far") or 0)
    rd_ios = float(disk_io_latest_values.get("rd_ios_so_far") - (disk_io_so_far_dict.get("rd_ios_so_far") or 0))
    rd_merges = float(disk_io_latest_values.get("rd_merges_so_far") - (disk_io_so_far_dict.get("rd_merges_so_far") or 0))
    rd_sectors = float(disk_io_latest_values.get("rd_sectors_so_far") - (disk_io_so_far_dict.get("rd_sectors_so_far") or 0))
    rd_ticks = float(disk_io_latest_values.get("rd_ticks_so_far") - (disk_io_so_far_dict.get("rd_ticks_so_far") or 0))
    wr_ios = float(disk_io_latest_values.get("wr_ios_so_far") - (disk_io_so_far_dict.get("wr_ios_so_far") or 0))
    wr_merges = float(disk_io_latest_values.get("wr_merges_so_far") - (disk_io_so_far_dict.get("wr_merges_so_far") or 0))
    wr_sectors = float(disk_io_latest_values.get("wr_sectors_so_far") - (disk_io_so_far_dict.get("wr_sectors_so_far") or 0))
    wr_ticks = float(disk_io_latest_values.get("wr_ticks_so_far") - (disk_io_so_far_dict.get("wr_ticks_so_far") or 0))
    time_in_queue = disk_io_latest_values.get("time_in_queue_so_far") - (disk_io_so_far_dict.get("time_in_queue_so_far") or 0)

    read_req = rd_ios / time_interval
    write_req = wr_ios / time_interval
    rkB = rd_sectors / disk_io_so_far_dict.get("sector_conversion_fctr") / time_interval
    wkB = wr_sectors / disk_io_so_far_dict.get("sector_conversion_fctr") / time_interval
    rrqm = rd_merges / time_interval
    wrqm = wr_merges / time_interval
    rrqm_perc = rd_merges * 100 / (rd_merges + rd_ios) if (rd_merges + rd_ios) else 0.0
    wrqm_perc = wr_merges * 100 / (wr_merges + wr_ios) if (wr_merges + wr_ios) else 0.0
    r_await = rd_ticks / rd_ios if rd_ios else 0.0
    w_await = wr_ticks / wr_ios if wr_ios else 0.0
    aqu_sz = time_in_queue / 1000.0
    rareq_sz = rd_sectors / disk_io_so_far_dict.get("sector_conversion_fctr") / rd_ios if rd_ios else 0.0
    wareq_sz = wr_sectors / disk_io_so_far_dict.get("sector_conversion_fctr") / wr_ios if wr_ios else 0.0
    svctm = 0
    # TODO calculate utils if needed in future
    util = 0

    # return time_sec, rd_ios_value, rd_merges_value, rd_sectors_value, rd_ticks_value, wr_ios_value, wr_merges_value, wr_sectors_value, wr_ticks_value, time_in_queue_value
    return read_req, write_req, rkB, wkB, rrqm, wrqm, rrqm_perc, wrqm_perc, r_await, w_await, aqu_sz, rareq_sz, wareq_sz, svctm, util, disk_io_latest_values

