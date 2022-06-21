import traceback


def process_event_v2(data, db_connection, db_name):
    try:
        # print(data)
        time_stamp_sec = int(data["data"]["time_stamp"])
        data["time_stamp_sec"] = time_stamp_sec
        logs_collection = db_connection[db_name].logs
        insert_id = logs_collection.insert_one(data).inserted_id


        # time_stamp_sec = int(data["data"]["time_stamp"])
        # data["time_stamp_sec"] = time_stamp_sec
        # transfer_collection = db_connection[db_name].logs
        # if data["is_sender"] == 1:
        #     query = {"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec}
        #     update = {"$set": {"is_sender": -1,
        #                        "sequence_number": data["sequence_number"],
        #                        "sender_data": data["data"],
        #                        "time_stamp_sec": time_stamp_sec,
        #                        "transfer_ID": data["transfer_ID"]}}
        #     transfer_collection.update_one(query, update, upsert=True)
        # else:
        #     query = {"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec}
        #     update = {"$set": {"is_sender": -1,
        #                        "sequence_number": data["sequence_number"],
        #                        "receiver_data": data["data"],
        #                        "time_stamp_sec": time_stamp_sec,
        #                        "transfer_ID": data["transfer_ID"]}}
        #     transfer_collection.update_one(query, update, upsert=True)


        # log = logs_collection.find_one({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
        # if log:
        #     d1 = log["data"]
        #     d2 = data["data"]
        #     d2.update(d1)
        #     data["is_sender"] = -1
        #     data["data"] = d2
        #
        #     query = {"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec}
        #     update = {"$set": {"is_sender": -1, "sequence_number": data["sequence_number"], "data": d2, "time_stamp_sec": time_stamp_sec, "transfer_ID": data["transfer_ID"]}}
        #     logs_collection.update_one(query, update, upsert=True)
        # else:
        #     insert_id = logs_collection.insert_one(data).inserted_id



        # def callback(session, db_name, t_id, time):
        #     logs_collection = session.client[db_name].logs
        #     print(t_id, time)
        #     all_logs_count = logs_collection.count_documents({"transfer_ID": t_id, "time_stamp_sec": time})
        #     if all_logs_count == 2:
        #         all_logs = logs_collection.find({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
        #         d_0 = all_logs[0]["data"]
        #         d_1 = all_logs[1]["data"]
        #         d_1.update(d_0)
        #         print(d_1)
        #         # print(d_0)
        #         # print(d_1, "\n")
        #         # data_array = []
        #         # for l in all_logs:
        #         #     data_array.append(l["data"])
        #         # data_array[1].update(data_array[0])
        #         # all_logs[1]["data"].update(all_logs[0]["data"])
        #         # print(all_logs[1]["data"])
        #         # print(all_logs[0]["data"])
        #         # logs_collection.update_one({"_id": all_logs[1]["_id"]}, all_logs[1])
        #         logs_collection.delete_one({"_id": all_logs[0]["_id"]})
        #         # logs_collection.delete_one({"_id": all_logs[1]["_id"]})
        #
        #
        # with db_connection.start_session() as session:
        #     session.with_transaction(
        #         lambda s: callback(s, db_name=db_name, t_id=data["transfer_ID"], time=time_stamp_sec)
        #         # read_concern=ReadConcern("local"),
        #         # write_concern=wc_majority,
        #         # read_preference=ReadPreference.PRIMARY,
        #     )


        # print(all_logs.count())
        # all_logs_count = logs_collection.count_documents({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
        # all_logs = logs_collection.find({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
        # print(data["transfer_ID"], time_stamp_sec, all_logs_count)
        # if all_logs_count == 2:
        #     all_logs = logs_collection.find({"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec})
        #     d_0 = all_logs[0]["data"]
        #     d_1 = all_logs[1]["data"]
        #     print(d_0)
        #     print(d_1, "\n")
        # data_array = []
        # for l in all_logs:
        #     data_array.append(l["data"])
        # data_array[1].update(data_array[0])
        # all_logs[1]["data"].update(all_logs[0]["data"])
        # print(all_logs[1]["data"])
        # print(all_logs[0]["data"])
        # logs_collection.update_one({"_id": data_array[1]["_id"]}, data_array[1])
        # logs_collection.delete_one({"_id": data_array[0]["_id"]})

    except Exception as e:
        traceback.print_exc()
