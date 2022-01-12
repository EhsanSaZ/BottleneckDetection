import time
from subprocess import Popen, PIPE


class DiskStatisticsLogCollector:
    def __init__(self, drive_name, sector_conversion_fctr=2):
        self.drive_name = drive_name

        self.time_interval = 0
        self.time_so_far = 0
        self.rd_ios = 0
        self.rd_ios_so_far = 0
        self.rd_merges = 0
        self.rd_merges_so_far = 0
        self.rd_sectors = 0
        self.rd_sectors_so_far = 0
        self.rd_ticks = 0
        self.rd_ticks_so_far = 0
        self.wr_ios = 0
        self.wr_ios_so_far = 0
        self.wr_merges = 0
        self.wr_merges_so_far = 0
        self.wr_sectors = 0
        self.wr_sectors_so_far = 0
        self.wr_ticks = 0
        self.wr_ticks_so_far = 0
        self.time_in_queue = 0
        self.time_in_queue_so_far = 0
        self.sector_conversion_fctr = sector_conversion_fctr

        self.response = ""
        self.time_sec = 0

    def execute_command(self):
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
        # # print(read_req," ",write_req," ",rkB," ",wkB," ",rrqm," ",wrqm," ",rrqm_perc," ",wrqm_perc," ",r_await," ",
        # w_await," ",areq_sz," ",rareq_sz," ",wareq_sz," ",svctm," ",util)
        proc = Popen(['cat', '/sys/block/{drive_name}/stat'.format(drive_name=self.drive_name)],
                     universal_newlines=True, stdout=PIPE)
        self.response = proc.communicate()[0]
        self.time_sec = time.time()

    def parse_output(self):
        parts = self.response.split()
        parts_filtered = list(filter(None, parts))
        disk_io_latest_values = {"sector_conversion_fctr": 2, "time": self.time_sec,
                                 "rd_ios": float(parts_filtered[0]),
                                 "rd_merges": float(parts_filtered[1]),
                                 "rd_sectors": float(parts_filtered[2]),
                                 "rd_ticks": float(parts_filtered[3]),
                                 "wr_ios": float(parts_filtered[4]),
                                 "wr_merges": float(parts_filtered[5]),
                                 "wr_sectors": float(parts_filtered[6]),
                                 "wr_ticks": float(parts_filtered[7]),
                                 "time_in_queue": float(parts_filtered[10])}
        # print(self.time_interval)
        self.time_interval = disk_io_latest_values.get("time") - self.time_so_far
        self.time_so_far = disk_io_latest_values.get("time")

        self.rd_ios = float(disk_io_latest_values.get("rd_ios") - self.rd_ios_so_far)
        self.rd_ios_so_far = disk_io_latest_values.get("rd_ios")

        self.rd_merges = float(disk_io_latest_values.get("rd_merges") - self.rd_merges_so_far)
        self.rd_merges_so_far = disk_io_latest_values.get("rd_merges")

        self.rd_sectors = float(disk_io_latest_values.get("rd_sectors") - self.rd_sectors_so_far)
        self.rd_sectors_so_far = disk_io_latest_values.get("rd_sectors")

        self.rd_ticks = float(disk_io_latest_values.get("rd_ticks") - self.rd_ticks_so_far)
        self.rd_ticks_so_far = disk_io_latest_values.get("rd_ticks")

        self.wr_ios = float(disk_io_latest_values.get("wr_ios") - self.wr_ios_so_far)
        self.wr_ios_so_far = disk_io_latest_values.get("wr_ios")

        self.wr_merges = float(disk_io_latest_values.get("wr_merges") - self.wr_merges_so_far)
        self.wr_merges_so_far = disk_io_latest_values.get("wr_merges")

        self.wr_sectors = float(disk_io_latest_values.get("wr_sectors") - self.wr_sectors_so_far)
        self.wr_sectors_so_far = disk_io_latest_values.get("wr_sectors")

        self.wr_ticks = float(disk_io_latest_values.get("wr_ticks") - self.wr_ticks_so_far)
        self.wr_ticks_so_far = disk_io_latest_values.get("wr_ticks")

        self.time_in_queue = disk_io_latest_values.get("time_in_queue") - self.time_in_queue_so_far
        self.time_in_queue_so_far = disk_io_latest_values.get("time_in_queue")

        # print(disk_io_latest_values.get("rd_ios"), self.rd_ios_so_far)
    def get_log_str(self):
        self.execute_command()
        self.parse_output()
        read_req = self.rd_ios / self.time_interval
        write_req = self.wr_ios / self.time_interval
        rkB = self.rd_sectors / self.sector_conversion_fctr / self.time_interval
        wkB = self.wr_sectors / self.sector_conversion_fctr / self.time_interval
        rrqm = self.rd_merges / self.time_interval
        wrqm = self.wr_merges / self.time_interval
        rrqm_perc = self.rd_merges * 100 / (self.rd_merges + self.rd_ios) if (self.rd_merges + self.rd_ios) else 0.0
        wrqm_perc = self.wr_merges * 100 / (self.wr_merges + self.wr_ios) if (self.wr_merges + self.wr_ios) else 0.0
        r_await = self.rd_ticks / self.rd_ios if self.rd_ios else 0.0
        w_await = self.wr_ticks / self.wr_ios if self.wr_ios else 0.0
        aqu_sz = self.time_in_queue / 1000.0
        rareq_sz = self.rd_sectors / self.sector_conversion_fctr / self.rd_ios if self.rd_ios else 0.0
        wareq_sz = self.wr_sectors / self.sector_conversion_fctr / self.wr_ios if self.wr_ios else 0.0
        svctm = 0
        # TODO calculate utils if needed in future
        util = 0

        return str(read_req) + "," + str(write_req) + "," + str(rkB) + "," + str(wkB) + "," + str(rrqm) + "," + \
               str(wrqm) + "," + str(rrqm_perc) + "," + str(wrqm_perc) + "," + str(r_await) + "," + str(w_await) + \
               "," + str(aqu_sz) + "," + str(rareq_sz) + "," + str(wareq_sz) + "," + str(svctm) + "," + str(util)
