
class Config:
    detection_server_host_ip = "*"
    detection_server_port = "50000"
    process_worker_number = 10
    streaming_thread_per_worker_process = 50

    db_address = 'localhost'
    db_port = '27017'
    db_name = 'testdb'
    db_user = 'mongoadmin'
    db_pass = 'mongoadmin'
