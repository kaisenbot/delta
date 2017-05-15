import psutil

def host_info():
    """Returns list containing:
    float: cpu usage (%)
    int: thread count
    int: phys core count
    int: rounded available mem (Mb)
    """
    host_info = [
        psutil.cpu_percent(interval=3),
        psutil.cpu_count(logical=True),
        psutil.cpu_count(),
        round(psutil.virtual_memory().free/1024**2),
        ]
    return host_info
