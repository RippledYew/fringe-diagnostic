#!/usr/bin/env python3
import sys
sys.path.insert(0, 'home/ripple/python/ecfm')
import ecfm_runner as er

configs = [
    {"probe_id": "p010", "probe_name": "lock_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 5000},
    {"probe_id": "p011", "probe_name": "lock_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 7500},
    {"probe_id": "p012", "probe_name": "lock_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 10000},
    {"probe_id": "p013", "probe_name": "lock_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 12500},
    {"probe_id": "p014", "probe_name": "lock_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 15000},
    {"probe_id": "p015", "probe_name": "lock_hunt", "N": 28, "eta": 0.75, "seed": 0, "steps": 20000},
    
]

for config in configs:
    result = er.run_probe(config)
    print(er.summarize(result))
    