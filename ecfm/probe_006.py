#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ripple/python/ecfm')
import ecfm_runner as er
import probe_logger

configs = [
    {"probe_id": "p026", "probe_name": "f_spike_zoom", "N": 28, "ets": 0.75, "seed": 0, "steps": 30000},
    {"probe_id": "p027", "probe_name": "f_spike_zoom", "N": 28, "ets": 0.75, "seed": 0, "steps": 31000},
    {"probe_id": "p028", "probe_name": "f_spike_zoom", "N": 28, "ets": 0.75, "seed": 0, "steps": 32000},
    {"probe_id": "p029", "probe_name": "f_spike_zoom", "N": 28, "ets": 0.75, "seed": 0, "steps": 33000},
    {"probe_id": "p030", "probe_name": "f_spike_zoom", "N": 28, "ets": 0.75, "seed": 0, "steps": 34000},
]

for config in configs:
    result = er.run_probe(config)
    print(er.summarize(result))
    probe_logger.log_probe(
        config["probe_id"],
        config,
        {"summary": er.summarize(result)}
    )