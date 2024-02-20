#!/pbs/throng/grand/soft/miniconda3/bin/python
import numpy as np

def extract_trigger_parameters(trace, trigger_config, baseline=0):
    # Extrace the trigger infos from a trace

    # Parameters :
    # ------------
    # trace, numpy.ndarray: 
    # traces in ADC unit
    # trigger_config, dict:
    # the nine trigger parameters set in DAQ

    # Returns :
    # ---------
    # Index in the trace when the first T1 crossing happens
    # Indices in the trace of T2 crossing happens
    # Number of T2 crossings
    # Q, Peak/NC

    # Find the position of the first T1 crossing
    index_t1_crossing = np.where(np.abs(trace) > trigger_config["th1"],
                                 np.arange(len(trace)), -1)
    dict_trigger_infos = dict()
    mask_T1_crossing = (index_t1_crossing != -1)
    if sum(mask_T1_crossing) == 0:
        # No T1 crossing 
        raise ValueError("No T1 crossing!")
    dict_trigger_infos["index_T1_crossing"] = index_t1_crossing[mask_T1_crossing][0]
    # The trigger logic works for the timewindow given by T_period after T1 crossing.
    # Count number of T2 crossings, relevant pars: T2, NCmin, NCmax, T_sepmax
    # From ns to index, divided by two for 500MHz sampling rate
    period_after_T1_crossing = trace[dict_trigger_infos["index_T1_crossing"]:dict_trigger_infos["index_T1_crossing"]+trigger_config['t_period']//2]
    # All the points above +T2
    positive_T2_crossing = (np.array(period_after_T1_crossing) > trigger_config['th2']).astype(int)
    # Positive crossing, the point before which is below T2.
    mask_T2_crossing_positive = np.diff(positive_T2_crossing) == 1
    # if np.sum(mask_T2_crossing_positive) > 0:
    #     index_T2_crossing_positive = np.arange(len(period_after_T1_crossing) - 1)[mask_T2_crossing_positive]
    negative_T2_crossing = (np.array(period_after_T1_crossing) < - trigger_config['th2']).astype(int)
    mask_T2_crossing_negative = np.diff(negative_T2_crossing) == 1
    # if np.sum(mask_T2_crossing_negative) > 0:
    #     index_T2_crossing_negative = np.arange(len(period_after_T1_crossing) - 1)[mask_T2_crossing_negative]
    # n_T2_crossing_negative = np.len(index_T2_crossing_positive)
    # Register the first T1 crossing as a T2 crossing
    mask_first_T1_crossing = np.zeros(len(period_after_T1_crossing), dtype=bool)
    mask_first_T1_crossing[0] = True
    mask_first_T1_crossing[1:] = (mask_T2_crossing_positive | mask_T2_crossing_negative)
    index_T2_crossing = np.arange(len(period_after_T1_crossing))[mask_first_T1_crossing]
    sep_T2_crossing = np.diff(index_T2_crossing)
    n_T2_crossing = 1 # Starting from the first T1 crossing.
    dict_trigger_infos["index_T2_crossing"] = [0]
    for i, j in zip(index_T2_crossing[:-1], index_T2_crossing[1:]):
        # The separation between successive T2 crossings
        time_separation = (j - i) * 2
        if time_separation <= trigger_config["t_sepmax"]:
            n_T2_crossing += 1
            dict_trigger_infos["index_T2_crossing"].append(j)
        else:
            # Violate the maximum separation, stop counting NC
            # Save the position of the last T2 crossing, i.e., i
            # to be used for calculating the Q value
            break
    dict_trigger_infos["NC"] = n_T2_crossing
    # Calulate the peak value
    dict_trigger_infos["Q"] = (np.max(np.abs(period_after_T1_crossing[:j])) - baseline) / dict_trigger_infos["NC"]
    return dict_trigger_infos

dict_trigger_parameter = dict([
("t_quiet", 512),
("t_period", 512),
("t_sepmax", 20),
("nc_min", 0),
("nc_max", 10),
("q_min", 0),
("q_max", 255),
("th1", 60),
("th2", 30),
# Configs of readout timewindow
("t_pretrig", 960),
("t_overlap", 64),
("t_posttrig", 1024)
])


# Read the traces from experimental data

# Zero padding at first

# Check if trigger
try:
  trigger_infos = extract_trigger_parameters(trace_padded, dict_trigger_parameter)
  # Save the triggered traces
except ValueError:
  # No T1 crossing, no trigger
    