#!/usr/bin/env python3
import sys
sys.path.insert(0, 'home/ripple/python/ecfm')
import ecfm_runner as er
import probe_logger

configs = [
    {"probe_id": "p021", "probe_name": "f_spike_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 20000},
    {"probe_id": "p022", "probe_name": "f_spike_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 25000},
    {"probe_id": "p023", "probe_name": "f_spike_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 30000},
    {"probe_id": "p024", "probe_name": "f_spike_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 35000},
    {"probe_id": "p025", "probe_name": "f_spike_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 40000},
]

for config in configs:
    result = er.run_probe(config)
    print(er.summarize(result))
    probe_logger.log_probe(
        config["probe_id"],
        config,
        {"summary": er.summarize(result)}
    )