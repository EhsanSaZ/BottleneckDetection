import time
from subprocess import Popen, PIPE


def get_disk_stat(drive_name):
    # global drive_name
    proc = Popen(['cat', '/sys/block/{drive_name}/stat'.format(drive_name=drive_name)], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
    time_sec = time.time()
    parts = res.split()
    parts_filtered = list(filter(None, parts))

    rd_ios = parts_filtered[0]  # number of read I/Os processed
    rd_merges = parts_filtered[1]  # number of read I/Os merged with in-queue I/O
    rd_sectors = parts_filtered[2]  # number of sectors read
    rd_ticks = parts_filtered[3]  # total wait time for read requests
    wr_ios = parts_filtered[4]  # number of write I/Os processed
    wr_merges = parts_filtered[5]  # number of write I/Os merged with in-queue I/O
    wr_sectors = parts_filtered[6]  # number of sectors written
    wr_ticks = parts_filtered[7]  # total wait time for write requests
    # in_flight = parts_filtered[8]  # number of I/Os currently in flight
    # io_ticks = parts_filtered[9]  # total time this block device has been active
    # time_in_queue = parts_filtered[10]  # total wait time for all requests
    # d_ios = parts_filtered[11]  # number of discard I/Os processed
    # d_merges = parts_filtered[12]  # number of discard I/Os merged with in-queue I/O
    # d_sectors = parts_filtered[13]  # number of sectors discarded
    # d_ticks = parts_filtered[14]  # total wait time for discard requests
    # fl_ios = parts_filtered[15]  # number of flush I/Os processed
    # fl_ticks = parts_filtered[16]  # total wait time for flush requests

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
    # return read_req, write_req, rkB, wkB, rrqm, wrqm, rrqm_perc, wrqm_perc, r_await, w_await, areq_sz, rareq_sz, wareq_sz, svctm, util
    return time_sec, rd_ios, rd_merges, rd_sectors, rd_ticks, wr_ios, wr_merges, wr_sectors, wr_ticks
