#1/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ripple/python/ecfm')
import ecfm_runner as er

configs = [
    {"probe_id": "p016", "probe_name": "seed_sweep", "N": 28, "ets": 0.75, "seed": 0, "steps": 50000},
    {"probe_id": "p017", "probe_name": "seed_sweep", "N": 28, "ets": 0.75, "seed": 1, "steps": 50000},
    {"probe_id": "p018", "probe_name": "seed_sweep", "N": 28, "ets": 0.75, "seed": 2, "steps": 50000},
    {"probe_id": "p019", "probe_name": "seed_sweep", "N": 28, "ets": 0.75, "seed": 3, "steps": 50000},
    {"probe_id": "p020", "probe_name": "seed_sweep", "N": 28, "ets": 0.75, "seed": 4, "steps": 50000},
]

for config in configs:
    result = er.run_probe(config)
    print(er.summarize(result))
    