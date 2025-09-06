import os
import matplotlib.pyplot as plt

def bar_distribution(metrics, title, out_png):
    cats = ["Compliant", "Partial", "Non-Compliant"]
    vals = [metrics["compliant"], metrics["partial"], metrics["noncompliant"]]
    plt.figure(figsize=(6,4))
    plt.bar(cats, vals)
    plt.title(title)
    plt.ylabel("Controls")
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close()
