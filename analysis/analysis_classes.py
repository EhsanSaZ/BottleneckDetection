from dataset_generator.bottleneck_pb2 import *
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn import svm
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.linear_model import SGDClassifier

from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
from IPython.core.display import display, HTML
from collections import Counter
import seaborn as sns  # to plot graphs

import time
import random as rd
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn import tree


class TransferAnalysis:
    def __init__(self, filename):
        self.bottleneck_logs = BottleneckFiles()
        self.log_type = "normal" if "FXS" not in filename else "luster"
        self.log_type = "cc"
        try:
            with open(filename, 'rb') as bfile:
                self.bottleneck_logs.ParseFromString(bfile.read())
        except IOError:
            print("File with name " + filename + " can't be opened")
        self.id_to_attr = {1: 'avg_rtt_value', 2: 'pacing_rate', 3: 'cwnd_rate', 4: 'avg_retransmission_timeout_value',
                           5: 'byte_ack', 6: 'seg_out', 7: 'retrans', 8: 'mss_value', 9: 'ssthresh_value',
                           10: 'segs_in', 11: 'avg_send_value', 12: 'unacked_value', 13: 'rcv_space',
                           14: 'send_buffer_value', 15: 'read_req', 16: 'write_req', 17: 'rkB', 18: 'wkB', 19: 'rrqm',
                           20: 'wrqm', 21: 'rrqm_perc', 22: 'wrqm_perc', 23: 'r_await', 24: 'w_await', 25: 'aqu_sz',
                           26: 'rareq_sz', 27: 'wareq_sz', 28: 'svctm', 29: 'util', 30: 'rchar', 31: 'wchar',
                           32: 'syscr', 33: 'syscw', 34: 'read_bytes_io', 35: 'write_bytes_io',
                           36: 'cancelled_write_bytes', 37: 'pid', 38: 'ppid', 39: 'pgrp', 40: 'session', 41: 'tty_nr',
                           42: 'tpgid', 43: 'flags', 44: 'minflt', 45: 'cminflt', 46: 'majflt', 47: 'cmajflt',
                           48: 'utime', 49: 'stime', 50: 'cutime', 51: 'cstime', 52: 'priority', 53: 'nice',
                           54: 'num_threads', 55: 'itrealvalue', 56: 'starttime', 57: 'vsize', 58: 'rss', 59: 'rsslim',
                           60: 'startcode', 61: 'endcode', 62: 'startstack', 63: 'kstkesp', 64: 'kstkeip', 65: 'signal',
                           66: 'blocked', 67: 'sigignore', 68: 'sigcatch', 69: 'wchan', 70: 'nswap', 71: 'cnswap',
                           72: 'exit_signal', 73: 'processor', 74: 'rt_priority', 75: 'policy',
                           76: 'delayacct_blkio_ticks', 77: 'guest_time', 78: 'cguest_time', 79: 'start_data',
                           80: 'end_data', 81: 'start_brk', 82: 'arg_start', 83: 'arg_end', 84: 'env_start',
                           85: 'env_end', 86: 'exit_code', 87: 'cpu_usage_percentage', 88: 'mem_usage_percentage',
                           89: 'tcp_rcv_buffer_min', 90: 'tcp_rcv_buffer_default', 91: 'tcp_rcv_buffer_max',
                           92: 'tcp_snd_buffer_min', 93: 'tcp_snd_buffer_default', 94: 'tcp_snd_buffer_max',
                           95: 'req_waittime', 96: 'req_active', 97: 'read_bytes', 98: 'write_bytes', 99: 'ost_setattr',
                           100: 'ost_read', 101: 'ost_write', 102: 'ost_get_info', 103: 'ost_connect', 104: 'ost_punch',
                           105: 'ost_statfs', 106: 'ost_sync', 107: 'ost_quotactl', 108: 'ldlm_cancel', 109: 'obd_ping',
                           110: 'pending_read_pages', 111: 'read_RPCs_in_flight', 112: 'avg_waittime_md1',
                           113: 'inflight_md1', 114: 'unregistering_md1', 115: 'timeouts_md1', 116: 'req_waittime_md1',
                           117: 'req_active_md1', 118: 'mds_getattr_md1', 119: 'mds_getattr_lock_md1',
                           120: 'mds_close_md1', 121: 'mds_readpage_md1', 122: 'mds_connect_md1',
                           123: 'mds_get_root_md1', 124: 'mds_statfs_md1', 125: 'mds_sync_md1', 126: 'mds_quotactl_md1',
                           127: 'mds_getxattr_md1', 128: 'mds_hsm_state_set_md1', 129: 'ldlm_cancel_md1',
                           130: 'obd_ping_md1', 131: 'seq_query_md1', 132: 'fld_query_md1', 133: 'close_md1',
                           134: 'create_md1', 135: 'enqueue_md1', 136: 'getattr_md1', 137: 'intent_lock_md1',
                           138: 'link_md1', 139: 'rename_md1', 140: 'setattr_md1', 141: 'fsync_md1',
                           142: 'read_page_md1', 143: 'unlink_md1', 144: 'setxattr_md1', 145: 'getxattr_md1',
                           146: 'intent_getattr_async_md1', 147: 'revalidate_lock_md1', 148: 'avg_waittime_md2',
                           149: 'inflight_md2', 150: 'unregistering_md2', 151: 'timeouts_md2', 152: 'req_waittime_md2',
                           153: 'req_active_md2', 154: 'mds_getattr_md2', 155: 'mds_close_md2', 156: 'mds_readpage_md2',
                           157: 'mds_connect_md2', 158: 'mds_statfs_md2', 159: 'mds_sync_md2', 160: 'mds_quotactl_md2',
                           161: 'mds_getxattr_md2', 162: 'mds_hsm_state_set_md2', 163: 'ldlm_cancel_md2',
                           164: 'obd_ping_md2', 165: 'seq_query_md2', 166: 'fld_query_md2', 167: 'close_md2',
                           168: 'create_md2', 169: 'enqueue_md2', 170: 'getattr_md2', 171: 'intent_lock_md2',
                           172: 'link_md2', 173: 'rename_md2', 174: 'setattr_md2', 175: 'fsync_md2',
                           176: 'read_page_md2', 177: 'unlink_md2', 178: 'setxattr_md2', 179: 'getxattr_md2',
                           180: 'intent_getattr_async_md2', 181: 'revalidate_lock_md2', 182: 'label_value'}

        if self.log_type == "normal":
            self.keys = list(range(1, 15)) + [44, 45, 46, 47, 48, 49, 50, 51, 54, 55, 57, 58, 59, 70, 71, 74, 76, 77,
                                              78] + list(range(87, 95)) + [182]  # list(range(1, 95)) + [182]
        elif self.log_type == "luster":
            self.keys = list(range(1, 15)) + [44, 45, 46, 47, 48, 49, 50, 51, 54, 55, 57, 58, 59, 70, 71, 74, 76, 77,
                                              78] + list(range(87, 183))
        else:
            self.keys = list(range(1, 95)) + [182]
        self.headers = [self.id_to_attr[i] for i in self.keys]
        self.get_dataframe_from_array()
        # self.remove_not_needed_cols() #To remove columns whose feature importance is close to 0

    def get_dataframe_from_array(self):
        log_list = []
        log_list_16 = []
        count = 0
        for file_ in self.bottleneck_logs.logs:
            count += len(file_.rows)
            for log in file_.rows:
                new_log = self.get_bottleneck_log_to_dict(log)
                log_list.append(new_log)

        self.df = pd.DataFrame(log_list)
        self.df_16 = pd.DataFrame(log_list_16, columns=self.headers)

    # T ODO what is this ??
    def get_bottleneck_log_to_dict(self, log):
        new_log = {}
        # print (len(self.keys))
        for i in self.keys:
            ##if new_log[self.id_to_attr[i]] == log.__getattribute__(self.id_to_attr[i]):
            # pass
            new_log[self.id_to_attr[i]] = log.__getattribute__(self.id_to_attr[i])
        return new_log

    def remove_not_needed_cols(self):
        new_list = ['retrans', 'mss_value', 'ssthresh_value', 'rcv_space', 'cminflt', 'cmajflt', 'cutime', 'cstime',
                    'num_threads', 'itrealvalue', 'vsize', 'rsslim', 'nswap', 'cnswap', 'rt_priority',
                    'delayacct_blkio_ticks', 'guest_time', 'cguest_time', 'tcp_rcv_buffer_min',
                    'tcp_rcv_buffer_default', 'tcp_rcv_buffer_max', 'tcp_snd_buffer_min', 'tcp_snd_buffer_default',
                    'tcp_snd_buffer_max', 'write_bytes', 'ost_write', 'ost_get_info', 'ost_punch', 'ost_statfs',
                    'ost_sync', 'ost_quotactl', 'pending_read_pages', 'read_RPCs_in_flight', 'inflight_md1',
                    'unregistering_md1', 'mds_getattr_md1', 'mds_readpage_md1', 'mds_connect_md1', 'mds_get_root_md1',
                    'mds_statfs_md1', 'mds_sync_md1', 'mds_quotactl_md1', 'mds_getxattr_md1', 'mds_hsm_state_set_md1',
                    'seq_query_md1', 'fld_query_md1', 'create_md1', 'enqueue_md1', 'getattr_md1', 'link_md1',
                    'rename_md1', 'fsync_md1', 'read_page_md1', 'setxattr_md1', 'getxattr_md1',
                    'intent_getattr_async_md1', 'avg_waittime_md2', 'inflight_md2', 'unregistering_md2', 'timeouts_md2',
                    'req_waittime_md2', 'req_active_md2', 'mds_getattr_md2', 'mds_close_md2', 'mds_readpage_md2',
                    'mds_connect_md2', 'mds_statfs_md2', 'mds_sync_md2', 'mds_quotactl_md2', 'mds_getxattr_md2',
                    'mds_hsm_state_set_md2', 'ldlm_cancel_md2', 'obd_ping_md2', 'seq_query_md2', 'fld_query_md2',
                    'close_md2', 'create_md2', 'enqueue_md2', 'getattr_md2', 'intent_lock_md2', 'link_md2',
                    'rename_md2', 'setattr_md2', 'fsync_md2', 'read_page_md2', 'unlink_md2', 'setxattr_md2',
                    'getxattr_md2', 'intent_getattr_async_md2', 'revalidate_lock_md2']
        new_list += ['ost_connect', 'mds_close_md1', 'ldlm_cancel_md1', 'revalidate_lock_md1', 'req_waittime_md1',
                     'unlink_md1', 'req_active', 'close_md1', 'mds_getattr_lock_md1', 'avg_waittime_md1',
                     'req_waittime', 'intent_lock_md1', 'obd_ping_md1', 'obd_ping', 'req_active_md1',
                     'mem_usage_percentage', 'ldlm_cancel', 'ost_read', 'unacked_value', 'read_bytes', 'ost_setattr',
                     'avg_retransmission_timeout_value', 'segs_in', 'setattr_md1']
        self.df.drop(new_list, axis=1, inplace=True)
        print("Generated DataFrame with %d rows and %d columns." % self.df.shape)


class Model_Run:
    def __init__(self):
        self.model_name = "RF"
        self.mlp_classifier = {"solver": "lbfgs", "hidden_layer_sizes": 10, "alpha": 1e-5, "max_iter": 1000,
                               "random_state": 0, "activation": "logistic", "learning_rate_init": 0.2
                               }

        self.model_to_name = {"RF": "Random Forest", "DT": "Decision Tree", "MLP": "MLP Classifier",
                              "KN": "KNeighborsClassifier", "QDA": "QuadraticDiscriminantAnalysis", "NB": "GaussianNB",
                              "ADA": "AdaBoostClassifier", "svm": "SVM", "sdg": "SGDClassifier"}

    def run_model(self, df, model_name=""):
        if not model_name:
            model_name = self.model_name
        df = df.sample(frac=1).reset_index(drop=True)
        X = df.drop(df.columns[len(df.columns) - 1], axis=1)
        Y = df[df.columns[len(df.columns) - 1]]
        total_labels = len(dict(Counter(Y)))

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=43)

        model_name_to_model = self.model_to_name

        clf = self.generate_with_all(X_train, y_train, model_name)
        y_pred = clf.predict(X_test)
        return metrics.accuracy_score(y_test, y_pred)

    def generate_with_all(self, X, y, model_name=""):
        if not model_name:
            model_name = self.model_name
        clf = None
        clf_data = self.get_mlp_classifier()
        total_labels = len(dict(Counter(y)))
        classifiers = {
            "kn": KNeighborsClassifier(3),
            "svc_kernel": SVC(kernel="linear", C=0.025),
            "svc": SVC(gamma=2, C=1),
            "gaussian": GaussianProcessClassifier(1.0 * RBF(1.0)),
            "dt": DecisionTreeClassifier(),

            "rf": RandomForestClassifier(n_estimators=total_labels, max_features="log2"),

            "mlp": MLPClassifier(solver=clf_data["solver"], hidden_layer_sizes=clf_data["hidden_layer_sizes"],
                                 alpha=clf_data["alpha"], max_iter=clf_data["max_iter"],
                                 random_state=clf_data["random_state"], activation=clf_data["activation"],
                                 learning_rate_init=clf_data["learning_rate_init"]),
            "ada": AdaBoostClassifier(),
            "nb": GaussianNB(),
            "qda": QuadraticDiscriminantAnalysis(),
            "svm": svm.SVC()}

        clf = classifiers[model_name.lower()]
        clf.fit(X, y)
        return clf

    def get_mlp_classifier(self):
        return self.mlp_classifier

    def set_mlp_classifier(self, clf_data={}):
        self.mlp_classifier = {"solver": "lbfgs", "hidden_layer_sizes": 10, "alpha": 1e-5, "max_iter": 150,
                               "random_state": 0, "activation": "logistic", "learning_rate_init": 0.2
                               }
        for i in clf_data:
            if i in self.mlp_classifier:
                self.mlp_classifier[i] = clf_data[i]

    def predict_with_other(self, clf, df):
        df = df.sample(frac=1).reset_index(drop=True)
        X = df.drop(df.columns[len(df.columns) - 1], axis=1)
        Y = df[df.columns[len(df.columns) - 1]]
        y_pred = clf.predict(X)
        return metrics.accuracy_score(Y, y_pred)

    def compare_two_dataset(self, df_a, df_b, model_name):
        if not model_name:
            model_name = self.model_name

        model_name_to_model = self.model_to_name
        print("")
        display(HTML("<b>Running Accuracy for %s</b>" % model_name_to_model[model_name]))

        df_a = df_a.sample(frac=1).reset_index(drop=True)
        X_a = df_a.drop(df_a.columns[len(df_a.columns) - 1], axis=1)
        y_a = df_a[df_a.columns[len(df_a.columns) - 1]]

        df_b = df_b.sample(frac=1).reset_index(drop=True)
        X_b = df_b.drop(df_b.columns[len(df_b.columns) - 1], axis=1)
        y_b = df_b[df_b.columns[len(df_b.columns) - 1]]

        clf_a = self.generate_with_all(X_a, y_a, model_name)
        clf_b = self.generate_with_all(X_b, y_b, model_name)

        display(HTML("<i>Run model with A and test with B</i>"))
        y_pred_b = clf_a.predict(X_b)
        print("\tAccuracy:", metrics.accuracy_score(y_b, y_pred_b))

        display(HTML("<i>Run model with B and test with A</i>"))
        y_pred_a = clf_b.predict(X_a)
        print("\tAccuracy:", metrics.accuracy_score(y_a, y_pred_a))

    def add_to_dataset(self, df, dataset_name="A", acc_df=[]):
        for model_name in ["RF", "DT", "MLP"]:
            acc_df.append({"DataSet": dataset_name, "Model": model_name, "Accuracy": cl.run_model(df_a, model_name)})
        return acc_df

    def plot_combined_acc(self, data_acc):
        sns.catplot(x="DataSet",  # x variable name
                    y="Accuracy",  # y variable name
                    hue="Model",  # group variable name
                    data=data_acc,  # dataframe to plot
                    kind="bar")
        plt.plot()

    def print_feature_importance(self, clf, df):
        data = {}
        features_importance = clf.feature_importances_
        feature_names = list(df.columns)[:-1]
        feature_sorted_index = [i[0] for i in sorted(enumerate(features_importance), key=lambda x: x[1], reverse=True)]

        for i in feature_sorted_index:
            data[feature_names[i]] = features_importance[i]
        return data

    def test_all_classifier(self, df):
        df = df.sample(frac=1).reset_index(drop=True)
        X = df.drop(df.columns[len(df.columns) - 1], axis=1)
        Y = df[df.columns[len(df.columns) - 1]]
        total_labels = len(dict(Counter(Y)))
        self.model_to_name = {"RF": "Random Forest", "DT": "Decision Tree", "MLP": "MLP Classifier",
                              "KN": "KNeighborsClassifier", "QDA": "QuadraticDiscriminantAnalysis", "NB": "GaussianNB",
                              "ADA": "AdaBoostClassifier", "svm": "SVM", "sdg": "SGDClassifier",
                              "pac": "PassiveAggressiveClassifier",

                              }
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=43)

        classifiers = {
            "kn": KNeighborsClassifier(3),
            "svc_kernel": SVC(kernel="linear", C=0.025),
            "svc": SVC(gamma=2, C=1),
            "gaussian": GaussianProcessClassifier(1.0 * RBF(1.0)),
            "dt": DecisionTreeClassifier(),
            "rf": RandomForestClassifier(n_estimators=total_labels, max_features=1),
            "mlp": MLPClassifier(alpha=1, max_iter=1000),
            "ada": AdaBoostClassifier(),
            "nb": GaussianNB(),
            "qda": QuadraticDiscriminantAnalysis(),
            "svm": svm.SVC(decision_function_shape='ovr'),
            "sdg": SGDClassifier(shuffle=True, loss='log'),
            "pac": PassiveAggressiveClassifier(max_iter=1000, random_state=0, tol=1e-3)
        }
        clsfier = ["kn", "rf", "dt", "qda"]
        for name_ in clsfier:
            clf = classifiers[name_].fit(X_train, y_train)
            print("[+] The accuracy for %s is %.5f" % (name_.upper(), clf.score(X_test, y_test)))

    def mlp_grid_search(self, df):
        df = df.sample(frac=1).reset_index(drop=True)
        X = df.drop(df.columns[len(df.columns) - 1], axis=1)
        Y = df[df.columns[len(df.columns) - 1]]
        total_labels = len(dict(Counter(Y)))

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=43)
        mlp = MLPClassifier(max_iter=100)
        parameter_space = {
            'hidden_layer_sizes': [(50, 50, 50), (50, 100, 50), (25, 25, 50, 25, 25)],
            'activation': ['tanh', 'relu'],
            'solver': ['sgd', 'adam'],
            'alpha': [0.0001, 0.05],
            'learning_rate': ['constant', 'adaptive'],
        }

        clf = GridSearchCV(mlp, parameter_space, n_jobs=-1, cv=3)
        clf.fit(X_train, y_train)
        # Best paramete set
        print('Best parameters found:\n', clf.best_params_)

        # All results
        means = clf.cv_results_['mean_test_score']
        stds = clf.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, clf.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))
        y_true, y_pred = y_test, clf.predict(X_test)

        from sklearn.metrics import classification_report
        print('Results on the test set:')
        print(classification_report(y_true, y_pred))

    def print_feature_imp(self, df, model_name=""):
        if not model_name:
            model_name = self.model_name
        df = df.sample(frac=1).reset_index(drop=True)
        X = df.drop(df.columns[len(df.columns) - 1], axis=1)
        Y = df[df.columns[len(df.columns) - 1]]
        total_labels = len(dict(Counter(Y)))

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=43)

        model_name_to_model = self.model_to_name

        clf = self.generate_with_all(X_train, y_train, model_name)
        data = self.print_feature_importance(clf, df)
        return data


class Grouped_Labels:
    def __init__(self):
        self.label_to_error = {0: "normal", 1: "read", 2: "read", 3: "read", 4: "read",
                               5: "read", 6: "read", 7: "read", 8: "read", 9: "read",
                               10: "read", 11: "read", 12: "read", 13: "read", 14: "read",
                               15: "read", 16: "read", 17: "write", 18: "write", 19: "write",
                               20: "write", 21: "write", 22: "write", 23: "write", 24: "write",
                               25: "write", 26: "write", 27: "write", 28: "write", 29: "write",
                               30: "write", 31: "write", 32: "write", 33: "cpu", 34: "io", 35: "mem",
                               36: "network", 37: "network", 38: "network", 39: "network",
                               40: "network", 41: "network", 42: "network", 43: "network", 44: "network",
                               45: "network", 46: "network", 47: "network", 48: "network", 49: "network",
                               50: "network", 51: "network", 52: "network", 53: "network", 54: "network", 55: "network"
                               }
        self.label_to_cate = {0: 0, 1: 1, 2: 1, 3: 1, 4: 1,
                              5: 1, 6: 1, 7: 1, 8: 1, 9: 1,
                              10: 1, 11: 1, 12: 1, 13: 1, 14: 1,
                              15: 1, 16: 1, 17: 2, 18: 2, 19: 2,
                              20: 2, 21: 2, 22: 2, 23: 2, 24: 2,
                              25: 2, 26: 2, 27: 2, 28: 2, 29: 2,
                              30: 2, 31: 2, 32: 2, 33: 4, 34: 5, 35: 6,
                              36: 7, 37: 7, 38: 7, 39: 7,
                              40: 8, 41: 8, 42: 8, 43: 8, 44: 9,
                              45: 9, 46: 9, 47: 9, 48: 10, 49: 10,
                              50: 10, 51: 10, 52: 11, 53: 11, 54: 11, 55: 11}

    def grouped_label(self, df):
        error_to_label = {"normal": 0, "read": 1, "write": 2, "cpu": 3, "io": 4, "mem": 5, "network": 6}
        y = [error_to_label[self.label_to_error[int(i)]] for i in df[df.columns[len(df.columns) - 1]].values]
        df["label_value"] = y
        return df

    def grouped_label_sin(self, df):
        error_to_label = {"normal": 0, "read": 1, "write": 1, "cpu": 2, "io": 1, "mem": 2, "network": 3}
        y = [error_to_label[self.label_to_error[int(i)]] for i in df[df.columns[len(df.columns) - 1]].values]
        df["label_value"] = y
        return df

    def grouped_label_ene(self, df):
        error_to_label = {"normal": 0, "read": 1, "write": 1, "cpu": 1, "io": 1, "mem": 1, "network": 1}
        y = [error_to_label[self.label_to_error[int(i)]] for i in df[df.columns[len(df.columns) - 1]].values]
        df["label_value"] = y
        return df

    def grouped_label_cate(self, df):
        y = [self.label_to_cate[int(i)] for i in df[df.columns[len(df.columns) - 1]].values]
        df["label_value"] = y
        return df

    def run_model(self, df, group_type="normal", model_name="RF"):
        new_df = df
        if group_type == "grouped":
            df = self.grouped_label_sin(df)
        elif group_type == "sin":
            df = self.grouped_label_sin(df)
        elif group_type == "ene":
            df = self.grouped_label_ene(df)
        else:
            df = df
        cl = Model_Run()
        return cl.run_model(df)


def get_Xy(df):
    df = df.sample(frac=1).reset_index(drop=True)
    X = df.drop(df.columns[len(df.columns) - 1], axis=1)
    Y = df[df.columns[len(df.columns) - 1]]
    return X, Y


def get_dfs():
    a = TransferAnalysis("../CSV-To-ProtoBuf/binary_logs/AWS_FXS/dataset_03152021_3")
    df_a = a.df

    b = TransferAnalysis("../CSV-To-ProtoBuf/binary_logs/AWS_FXS/dataset_03152021_2")
    df_b = b.df
    return df_b, df_a
