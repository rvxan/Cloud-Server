import time
import csv
import os


class networkAnalysis:
    files_dir = os.path.join(os.getcwd(), 'Files')
    if not os.path.exists(files_dir):
        os.mkdir(files_dir)
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = os.path.join(os.getcwd(), f"network_stats_{timestamp}.csv")

    def __init__(self):
        pass

    @staticmethod
    def create_csv():
        with open(networkAnalysis.file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Type', 'Upload/Download Rate (MB/s)', 'Transfer Time (s)'])

    @staticmethod
    def save_data(data):
        with open(networkAnalysis.file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

    @staticmethod
    def calculate_download(start_time, end_time, file_size):
        transfer_time = end_time - start_time
        if transfer_time > 0:
            transfer_rate = file_size / transfer_time / (1024 * 1024)
        else:
            transfer_rate = 0

        print(f"Download rate: {transfer_rate:.5f} MB/s")
        print(f"Transfer Time: {transfer_time:.5f}s")
        data = ['Download', transfer_rate, transfer_time]
        networkAnalysis.save_data(data)

    @staticmethod
    def calculate_upload(start_time, end_time, file_size):
        transfer_time = end_time - start_time
        if transfer_time > 0:
            transfer_rate = file_size / transfer_time / (1024 * 1024)
        else:
            transfer_rate = 0

        print(f"Upload rate: {transfer_rate:.5f} MB/s")
        print(f"Transfer Time: {transfer_time:.5f}s")
        data = ['Upload', transfer_rate, transfer_time]
        networkAnalysis.save_data(data)

    @staticmethod
    def calculate_latency(start_time, end_time):
        latency = (end_time - start_time) * 1000
        print(f"Latency: {latency:.5f}ms")
        data = ['Latency', latency]
        networkAnalysis.save_data(data)



