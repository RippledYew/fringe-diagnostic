#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ripple/python/ecfm")')
import probe_logger
import ecfm_runner as er

configs = [
    {"probe_id": "p001", "sweep_param": "sweep_eta", "N": 28, "eta": 0.50, "seed": 0, "steps": 400},
    {"probe_id": "p002", "sweep_param": "sweep_eta", "N": 28, "eta": 0.60, "seed": 0, "steps": 400},
    {"probe_id": "p003", "sweep_param": "sweep_eta", "N": 28, "eta": 0.75, "seed": 0, "steps": 400},
    {"probe_id": "p004", "sweep_param": "sweep_eta", "N": 28, "eta": 0.90, "seed": 0, "steps": 400},
]

for config in configs:
    result = er.run_probe(config)
    print(er.summarize(result))
    probe_logger.log_probe(
        config["probe_id"],
        config,
        {"summary": er.summarize(result)}
    )
    