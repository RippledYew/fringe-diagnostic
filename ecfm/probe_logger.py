#!/usr/bin/env python3
import json
import os
from datetime import datetime

LOG_FILE = "/home/ripple/python/ecfm/probe_log.json"

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return {"probes": [], "created": str(datetime.now())}

def save_log(log):
    with open(LOG_FILE, 'w') as f:
            json.dump(log, f, indent=2)
            
def log_probe(probe_id, config, result_summary):
    log = load_log()
    entry = {
        "probe_id": probe_id,
        "timestamp": str(datetime.now()),
        "config": config,
        "result": result_summary
    }
    log["probes"].append(entry)
    save_log(log)
    print(f"Logged: {probe_id}")
    
def show_log():
    log = load_log()
    print(f"Total probes logged: {len(log['probes'])}")
    for entry in log["probes"]:
        print(f"{entry['probe_id']} | {entry['timestamp']} | {entry['result']}")
        
if __name__ == "__main__":
    log_probe(
        "p_test",
        {"N": 28, "eta": 0.75, "seed": 0, "steps": 400},
         {"regime": "STD", "tau": 0.99, "cos_theta": 0.735, "curv_soc": 3.087}
    )
    show_log()