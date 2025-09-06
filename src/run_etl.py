import yaml
from src.etl import run_etl
from src.visuals import export_charts

if __name__ == "__main__":
    cfg = yaml.safe_load(open("config.yaml"))
    k1, k2 = run_etl(cfg)
    export_charts(k1, k2, cfg["output_folder"])
    print("Done. KPIs:", k1, k2)
