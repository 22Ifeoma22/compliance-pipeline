from pathlib import Path
import matplotlib.pyplot as plt

def _save_distribution(kpi, path):
    labels = ["Compliant (>=90)", "Partial (70-89)", "Non-compliant (<70)"]
    values = [kpi["green"], kpi["amber"], kpi["red"]]
    plt.figure()
    plt.bar(labels, values)       # no custom colors/styles per your rule
    plt.title("Control Distribution")
    plt.ylabel("Count")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(); plt.savefig(path); plt.show()


def export_charts(k1, k2, out_dir):
    _save_distribution(k1, f"{out_dir}/iso27001_distribution.png")
    _save_distribution(k2, f"{out_dir}/iso27701_distribution.png")
