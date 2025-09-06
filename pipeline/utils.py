import logging, os, time

def get_logger(name="pipeline"):
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename=f"logs/{name}.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    return logging.getLogger(name)

def timestamp():
    return time.strftime("%Y-%m-%d_%H-%M-%S")
