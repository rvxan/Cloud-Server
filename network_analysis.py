
def calculate_download(start_time, end_time, file_size):
    transfer_time = end_time - start_time
    if transfer_time > 0:
        transfer_rate = file_size / transfer_time / (1024 * 1024)
    else:
        transfer_rate = 0

    print(f"Download rate: {transfer_rate:.2f} MB/s")
    print(f"Transfer Time: {transfer_time}s")


def calculate_upload(start_time, end_time, file_size):
    transfer_time = end_time - start_time
    if transfer_time > 0:
        transfer_rate = file_size / transfer_time / (1024 * 1024)
    else:
        transfer_rate = 0

    print(f"Upload rate: {transfer_rate:.2f} MB/s")
    print(f"Transfer Time: {transfer_time}s")
