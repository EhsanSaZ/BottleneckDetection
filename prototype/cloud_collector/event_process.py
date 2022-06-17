import traceback


def process_event(data, db_connection, db_name):
    try:
        # print(data)
        time_stamp_sec = int(data["data"]["time_stamp"])
        data["time_stamp_sec"] = time_stamp_sec
        sender_collection = db_connection[db_name].senders_logs
        receiver_collection = db_connection[db_name].receiver_logs
        if data["is_sender"] == 1:
            # print("is sender", data["transfer_ID"], time_stamp_sec)
            sndr_insert_id = sender_collection.insert_one(data).inserted_id
            r_log = receiver_collection.find_one({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
            # print(r_log)
            if r_log:
                # print("MATCH found")
                # match both logs, insert them in to new collection and remove from first collections
                d1 = r_log["data"]
                d2 = data["data"]
                d2.update(d1)
                data["is_sender"] = -1
                data["data"] = d2
                print("Match with receiver", data["transfer_ID"], time_stamp_sec)
                transfer_collection = db_connection[db_name].transfer_logs
                query = {"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec}
                update = {"$set": {"is_sender": -1, "sequence_number": data["sequence_number"], "data": d2, "time_stamp_sec": time_stamp_sec, "transfer_ID": data["transfer_ID"]}}
                transfer_collection.update_one(query, update, upsert=True)
                # tr_insert_id = transfer_collection.insert_one(data).inserted_id
                sender_collection.delete_many({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
                receiver_collection.delete_many({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
            # else:
            #     sndr_insert_id = sender_collection.insert_one(data).inserted_id
        elif data["is_sender"] == 0:
            # sender_collection = db_connection[db_name].senders_logs
            # receiver_collection = db_connection[db_name].receiver_logs
            # print("is receiver", data["transfer_ID"], time_stamp_sec)
            rcv_insert_id = receiver_collection.insert_one(data).inserted_id
            s_log = sender_collection.find_one({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
            if s_log:
                # match both logs, insert them in to new collection and remove from first collections
                d1 = s_log["data"]
                d2 = data["data"]
                d2.update(d1)
                data["is_sender"] = -1
                data["data"] = d2
                print("Match with sender", data["transfer_ID"], time_stamp_sec)
                transfer_collection = db_connection[db_name].transfer_logs
                query = {"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec}
                update = {"$set": {"is_sender": -1, "sequence_number": data["sequence_number"], "data": d2, "time_stamp_sec": time_stamp_sec, "transfer_ID": data["transfer_ID"]}}
                transfer_collection.update_one(query, update, upsert=True)

                # tr_insert_id = transfer_collection.insert_one(data).inserted_id
                sender_collection.delete_many({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
                receiver_collection.delete_many({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
            # else:
            #     rcv_insert_id = receiver_collection.insert_one(data).inserted_id
    except Exception as e:
        traceback.print_exc()
