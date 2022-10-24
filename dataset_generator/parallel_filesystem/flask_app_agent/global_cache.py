from multiprocessing import Value, Array, Manager
manager = Manager()
ost_metrics_dict = manager.dict({})
