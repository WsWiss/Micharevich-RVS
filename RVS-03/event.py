import threading
import time
import random

NUM_WORKERS      = 5
SIGNAL_INTERVAL  = 3
event            = threading.Event()
print_lock       = threading.Lock()          # защита терминала

def safe_print(*args, **kw):
    """Потокобезопасный print."""
    with print_lock:
        print(*args, **kw)

def worker(w_id: int):
    while True:
        safe_print(f"[{w_id}] Поток уходит в ожидание")
        event.wait()
        safe_print(f"[{w_id}] Поток продолжил работу")
        time.sleep(0.5)

def controller():
    while True:
        time.sleep(SIGNAL_INTERVAL)
        safe_print(">>> Управляющий поток подаёт сигнал event.set()")
        event.set()
        time.sleep(SIGNAL_INTERVAL)
        event.clear()

if __name__ == "__main__":
    for i in range(1, NUM_WORKERS + 1):
        threading.Thread(target=worker, args=(i,), daemon=True).start()

    threading.Thread(target=controller, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        safe_print("\nПрограмма завершена пользователем")