from pipeline.etl import run
import yaml
from pipeline.notifier import send_email_graph   # <-- this one

CFG = "config.yaml"

def load_cfg(path=CFG):
    with open(path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    run()
    cfg = load_cfg()
    send_email_graph(cfg)    # <-- call the Graph sender
