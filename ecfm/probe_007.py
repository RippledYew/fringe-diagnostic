import sys
sys.path.insert(0, '/home/ripple/python/ecfm')
import ecfm_runner as er
import probe_logger

configs = [
    {"probe_id": "p031", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31000},
    {"probe_id": "p032", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31100},
    {"probe_id": "p033", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31200},
    {"probe_id": "p034", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31300},
    {"probe_id": "p035", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31400},
    {"probe_id": "p036", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31500},
    {"probe_id": "p037", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31600},
    {"probe_id": "p038", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31700},
    {"probe_id": "p039", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31800},
    {"probe_id": "p040", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 31900},
    {"probe_id": "p041", "probe_name": "f_spike_exact", "N": 28, "eta": 0.75, "seed": 0, "steps": 32000},
]

for config in configs:
    result = er.run_probe(config)
    print(er.summarize(result))
    probe_logger.log_probe(
        config["probe_id"],
        config,
        {"summary": er.summarize(result)}
    )
    