import traceback
from pymongo import ReturnDocument


def process_event_v3(data, db_connection, db_name):
    try:
        # print(data)
        time_stamp_sec = int(data["data"]["time_stamp"])
        data["time_stamp_sec"] = time_stamp_sec
        transfer_collection = db_connection[db_name].logs
        if data["is_sender"] == 1:
            query = {"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec}
            update = {"$set": {"is_sender": -1,
                               "sequence_number": data["sequence_number"],
                               "sender_data": data["data"],
                               "time_stamp_sec": time_stamp_sec,
                               "transfer_ID": data["transfer_ID"]}}
            # transfer_collection.update_one(query, update, upsert=True)
            doc = transfer_collection.find_one_and_update(query, update, upsert=True,
                                                          return_document=ReturnDocument.AFTER)
            # print(doc)
            # if doc.get("sender_data") and doc.get("receiver_data"):
            #     print(doc)
            #     print("OK, Run the machine learning prediction")
        else:
            query = {"transfer_ID": data["transfer_ID"], "time_stamp_sec": time_stamp_sec}
            update = {"$set": {"is_sender": -1,
                               "sequence_number": data["sequence_number"],
                               "receiver_data": data["data"],
                               "time_stamp_sec": time_stamp_sec,
                               "transfer_ID": data["transfer_ID"]}}
            # transfer_collection.update_one(query, update, upsert=True)
            doc = transfer_collection.find_one_and_update(query, update, upsert=True,
                                                          return_document=ReturnDocument.AFTER)
            # print(doc)
            # if doc.get("sender_data") and doc.get("receiver_data"):
            #     print(doc)
            #     print("OK, Run the machine learning prediction")

    except Exception as e:
        print(e)
        traceback.print_exc()
