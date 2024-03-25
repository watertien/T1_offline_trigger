import numpy as np

th1_pos_from_root = 700
trace_length = 1024
file_traces = np.genfromtxt("install/grand-daq-master_240319/wavelet_test.txt")


def grand_trigger_fv3(trace, trigger_config):
    # GRAND FLT-0 trigger logics
    # 
    # Parameters :
    # ---------------
    # wl: numpy.ndarray
    # The wavelet array (average or difference) of two
    # continuous points from the original trace.
    # 
    # trigger_config: dict
    # Trigger parameters used in the trigger decision
    # 
    # Returns:
    # dict_trigger_infos : dict
    # Dictionary with trigger infos:
    # position of T1&T2 pass
    # number of T2 pass
    # trigger flag: if trigger and the reason of no trigger, if any
    # flag:
    # 1: normal trigger
    # 0: no values above T1/T2
    # -1: separation between two >T2 points greater t_sepmax
    # -2: out of NC range

    # get the wavelet/diff trace
    wl = np.concatenate([[0], np.diff(trace)])
    wl = np.abs(wl) # absolute value of difference between points
    # Trigger logic copied from the Trigger.c
    t1position = -1 # postion of exceeding Th1
    t1passed = 0 # if in a trigger/pulse
    plength=0 # length of the pulse
    nc = 0 # number of points above Th2
    t2prev = -1 # if the prevous point is above Th2
    triggered_bool = 100 # if finishes the decision of trigger
    triggered_pos = 0 # position of traces when finishes the trigger logics
    th1 = trigger_config["th1"]
    dict_trigger_infos = {}
    index_T1 = []
    index_T2 = []
    for i in range(trace_length):
        if (i == (th1_pos_from_root - 10)):
            th1 -= 3
        if (i == (th1_pos_from_root + 10)):
            th1 += 3
        if t1passed:
            plength += 1
            isT2 = 0
            if wl[i] > trigger_config["th2"]:
                # Current point greater than Th2
                isT2 = 1
            if isT2:
                # if t2prev > 0: print(f"{i} - {t2prev} = {i - t2prev}")
                if ((t2prev > 0) & ((i - t2prev) > trigger_config["t_sepmax"] // 2)):
                    # the previous >T2 point exists, but the separation greater than t_sepmax
                    triggered_bool = -1
                # print(f"T2 ..., {t2prev}, {i}")
                t2prev = i # update t2prev to current index
                nc += 1 # increment the NC by 1
                index_T2.append(i)
                if ((nc > trigger_config["nc_max"]) | (nc < trigger_config["nc_min"])):
                    # TODO : for the first T2 crossing, this is always true?
                    # i.e. if NCmin > 0, then the condition is alway True
                    triggered_bool = -2 # violate the range of NC
            # print(i, plength)
            if plength == trigger_config["t_period"] // 2:
                # the end of pulse decision
                t1passed = 0 # reset the T1passed, starting to looking for next one
                if triggered_bool == 0:
                    triggered_bool = 1 # pass all conditions, set to 1
                    triggered_pos = i # index of statifying the whole pulse logic
                    # print("One trigger")
        if (wl[i] >= th1) & ((t1position < 0) | ((i - t1position) > trigger_config["t_quiet"] // 2)):
            # ADC above Th1 and statisfy the quiet condition
            # start to process the pulse to decide the trigger
            # reset all parameters
            t1passed = 1
            t1position = i
            plength = 0
            nc = 0
            t2prev = -1
            triggered_bool = 0
        if wl[i] >= th1:
            # print(f"T1 ..., {t1position}, {i}")
            t1position = i
            index_T1.append(i)
            index_T2 = []
            nc = 0
            t2prev = -1
    dict_trigger_infos["NC"] = nc
    dict_trigger_infos["Index_T1_crossing"] = index_T1
    dict_trigger_infos["Index_T2_crossing"] = index_T2
    dict_trigger_infos["trigger_flag"] = triggered_bool
    dict_trigger_infos["trigger_pos"] = triggered_pos # index where the trigger logics is satisfied.
    return dict_trigger_infos



if __name__ == "__main__":
    dict_trigger_parameter = dict([
    ("t_quiet", 0), # working
    ("t_period", 10), # working
    ("t_sepmax", 20), # working
    ("nc_min", 0), # not working, only 0 or 1 can be allowed, otherwise cannot trigger
    ("nc_max", 5), # working
    ("q_min", 0), # not used
    ("q_max", 255), # not used
    ("th1", 100), # working
    ("th2", 50), # working
    # Configs of readout timewindow
    ("t_pretrig", 960),
    ("t_overlap", 64),
    ("t_posttrig", 1024)
    ])
    trigger_infos = grand_trigger_fv3(file_traces[:,1], dict_trigger_parameter)
    print(trigger_infos)
