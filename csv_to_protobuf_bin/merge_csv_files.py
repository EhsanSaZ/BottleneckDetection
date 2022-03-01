import csv
import os
from pathlib import Path


class MergeCSVFiles:
    def __init__(self, sender_data_set_dir, receiver_data_set_dir, folder_name):
        self.sender_data_set_dir = sender_data_set_dir

        self.receiver_data_set_dir = receiver_data_set_dir
        self.folder_name = folder_name
        self.out_put_dir = "./csv_logs/AWS_FXS/{}/".format(self.folder_name)
        self.create_directory(self.out_put_dir)

    def create_directory(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)

    def read_csv_file(self, csv_path):
        data = []
        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                data.append(row)
        return data

    def convert_time_stamp_to_seconds(self, time_stamp_str):
        return int(time_stamp_str.split('.')[0]) 

    def merge_files(self, sender_file_name, receiver_file_name):
        sender_logs = self.read_csv_file(self.sender_data_set_dir + sender_file_name)
        receiver_logs = self.read_csv_file(self.receiver_data_set_dir + receiver_file_name)
        sender_total_logs = len(sender_logs)
        receiver_total_logs = len(receiver_logs)
        sender_log_index = 0
        receiver_log_index = 0
        merged_data = []

        for log in sender_logs:
            # get time stamp in seconds
            if receiver_log_index >= receiver_total_logs:
                break
            sender_time_stamp = self.convert_time_stamp_to_seconds(log[0])
            r_log = receiver_logs[receiver_log_index]
            receiver_time_stamp = self.convert_time_stamp_to_seconds(r_log[0])
            while sender_time_stamp > receiver_time_stamp and receiver_log_index < receiver_total_logs:
                receiver_log_index += 1
                r_log = receiver_logs[receiver_log_index]
                receiver_time_stamp = self.convert_time_stamp_to_seconds(r_log[0])
            if sender_time_stamp == receiver_time_stamp:
                # print("merging\n{}\n{}".format(log, r_log))
                sender_part = log[:-1]
                label_value = log[-2:-1]
                # omit time stamp and label value from first and last indices of r_log
                receiver_part = r_log[1:-1]
                merged_data.append(sender_part + receiver_part + label_value)
                receiver_log_index += 1
        return merged_data

    def merge_csv_files(self):
        sender_log_files = os.listdir(self.sender_data_set_dir)
        receiver_log_files = os.listdir(self.receiver_data_set_dir)
        for sender_filename in sender_log_files:
            if 'dataset_' in sender_filename and 'csv' in sender_filename and sender_filename in receiver_log_files:
                print("[+] Starting merging {}".format(sender_filename))
                merged_data = self.merge_files(sender_filename, sender_filename)
                self.write_csv_file(merged_data, sender_filename)
                # print(merged_data)

    def write_csv_file(self, logs_arr, csv_file_name):
        with open(self.out_put_dir + csv_file_name, 'w', newline='') as file:
            mywriter = csv.writer(file, delimiter=',')
            mywriter.writerows(logs_arr)


def get_correct_path(path):
    if not path.endswith('/'):
        return path + "/"
    else:
        return path

sender_logs_folder_name = "./unmerged_ds/series11/source/"
receiver_logs_folder_name = "./unmerged_ds/series11/destination/"
sender_logs_folder_name = get_correct_path(sender_logs_folder_name)
receiver_logs_folder_name = get_correct_path(receiver_logs_folder_name)
main_folder_name = sender_logs_folder_name.split("/")[-3]
merge_csv_obj = MergeCSVFiles(sender_logs_folder_name, receiver_logs_folder_name, main_folder_name)
merge_csv_obj.merge_csv_files()



