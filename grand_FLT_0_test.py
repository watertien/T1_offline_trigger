#!/pbs/home/x/xtian/.conda/envs/grandlib2304/bin/python3.9
import uproot as ur
from grand_FLT_0_trigger import *
import sys

if __name__ == "__main__":
  # Read the traces from experimental data
  fname = sys.argv[1]
  root_key_list = ["min_crossing_lim_ch",
  "max_crossing_lim_ch",
  "tmax_crossings_ch", 
  "signal_threshold_ch", 
  "noise_threshold_ch", 
  "tpre_trig_ch", 
  "tpre_trig_ch", 
  "tpost_trig_ch", 
  "trigger_status",
  'trace_ch']
  # Read trigger parameters from the entry.
  dict_trigger_parameter = dict([
  ("t_quiet", 512),
  ("t_period", 512),
  ("t_sepmax", 10),
  ("nc_min", 2),
  ("nc_max", 8),
  ("q_min", 0),
  ("q_max", 255),
  ("th1", 100),
  ("th2", 50),
  # Configs of readout timewindow
  ("t_pretrig", 960),
  ("t_overlap", 64),
  ("t_posttrig", 1024)
  ])
  trace_test = np.zeros((2, 1024), dtype=int)
  for j, event in enumerate(ur.iterate(fname + ":tadc", root_key_list, step_size=1)):
    # Loop over two channels
    list_trigger_times = [0, 0]
    for i in range(2):
      # Update trigger parameters
      dict_trigger_parameter["nc_min"] = event["min_crossing_lim_ch"][0][0][i]
      dict_trigger_parameter["nc_max"] = event["max_crossing_lim_ch"][0][0][i]
      dict_trigger_parameter["t_sepmax"] = event["tmax_crossings_ch"][0][0][i]
      dict_trigger_parameter["th1"] = event["signal_threshold_ch"][0][0][i] + 2 
      dict_trigger_parameter["th2"] = event["noise_threshold_ch"][0][0][i] + 2
      dict_trigger_parameter["t_quiet"] = event["tpre_trig_ch"][0][0][i]
      # dict_trigger_parameter["t_overlap"] = event[""]
      dict_trigger_parameter["t_period"] = event["tpost_trig_ch"][0][0][i]
      dict_trigger_parameter["trig_status"] = event["trigger_status"][0][0]
      trace = event["trace_ch"][0][0][i]
      trigger_infos = grand_trigger_fv3(trace, dict_trigger_parameter)
      list_trigger_times[i] = trigger_infos["trigger_times"]
    if sum(list_trigger_times) == 0:
      print(f"{fname}: {j}-th, No trigger")
