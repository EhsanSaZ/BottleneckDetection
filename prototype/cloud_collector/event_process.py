import traceback


def process_event(data, db_connection, db_name):
    try:
        print(data)
        time_stamp_sec = int(data["data"]["time_stamp"])
        data["time_stamp_sec"] = time_stamp_sec
        sender_collection = db_connection[db_name].senders_logs
        receiver_collection = db_connection[db_name].receiver_logs
        if data["is_sender"] == 1:
            sndr_insert_id = sender_collection.insert_one(data).inserted_id
            r_log = receiver_collection.find_one({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
            print(r_log)
            if r_log:
                # match both logs, insert them in to new collection and remove from first collections
                d1 = r_log["data"]
                d2 = data["data"]
                d2.update(d1)
                data["is_sender"] = -1
                data["data"] = d2

                transfer_collection = db_connection[db_name].transfer_logs
                tr_insert_id = transfer_collection.insert_one(data).inserted_id
                sender_collection.deleteMany({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
                receiver_collection.deleteMany({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})

        elif data["is_sender"] == 0:
            # sender_collection = db_connection[db_name].senders_logs
            # receiver_collection = db_connection[db_name].receiver_logs
            rcv_insert_id = receiver_collection.insert_one(data).inserted_id
            s_log = sender_collection.find_one({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
            if s_log:
                # match both logs, insert them in to new collection and remove from first collections
                d1 = s_log["data"]
                d2 = data["data"]
                d2.update(d1)
                data["is_sender"] = -1
                data["data"] = d2
                transfer_collection = db_connection[db_name].transfer_logs
                tr_insert_id = transfer_collection.insert_one(data).inserted_id
                sender_collection.deleteMany({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
                receiver_collection.deleteMany({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
    except Exception as e:
        traceback.print_exc()
