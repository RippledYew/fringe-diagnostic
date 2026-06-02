import sys
sys.path.insert(0, '/home/ripple/python/ecfm')
import ecfm_runner as er

configs = [
    {"probe_id": "p042", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31500},
    {"probe_id": "p043", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31510},
    {"probe_id": "p044", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31520},
    {"probe_id": "p045", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31530},
    {"probe_id": "p046", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31540},
    {"probe_id": "p047", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31550},
    {"probe_id": "p048", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31560},
    {"probe_id": "p049", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31570},
    {"probe_id": "p050", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31580},
    {"probe_id": "p051", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31590},
    {"probe_id": "p052", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31600},
]

for config in configs:
    result = er.run_probe(config)
    print(er.summarize(result))