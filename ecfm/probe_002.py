#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ripple/python/ecfm')
import ecfm_runner as er

configs = [
    {"probe_id": "p005", "probe_name": "Sweep_steps", "N": 28, "eta": 0.75, "seed": 0, "steps": 400},
    {"probe_id": "p006", "probe_name": "Sweep_steps", "N": 28, "eta": 0.75, "seed": 0, "steps": 1000},
    {"probe_id": "p007", "probe_name": "Sweep_steps", "N": 28, "eta": 0.75, "seed": 0, "steps": 5000},
    {"probe_id": "p008", "probe_name": "Sweep_steps", "N": 28, "eta":0.75, "seed": 0, "steps": 10000},
    {"probe_id": "p009", "probe_name": "Sweep_steps", "N": 28, "eta":0.75, "seed": 0, "steps": 50000},
]

for config in configs:
    result = er.run_probe(config)
    print(er.summarize(result))
    
 