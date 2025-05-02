import socket
import yaml,os,signal
from core.config import load_config
# from core.handler import handle_client
from core.logger import debug_log,log_print,clear_log
from core.worker import run_worker
from core.helper import get_routes

def spawn_worker(config, w_id):
    pid = os.fork()
    if pid == 0:
        # Child process
        # As from here new process started and pid is 0 that means child process creatd so use getpid
        w_data = {
            "w_pid": os.getpid(),  # Correctly get own PID
            "w_id": w_id,
            "status": True
        }
        run_worker(w_data, config)
        os._exit(0)

    # Parent process
    w_data = {
        "w_pid": pid,  # This is the actual child's PID
        "w_id": w_id,
        "status": True
    }
    return w_data



def run_server():
    print("Mini Nginx Started...")
    
    config = load_config()
    clear_log()

    # need to add parser so config file can validate
    config['available_routes'] = get_routes(config)

    debug_log(config)

    worker_count = config.get("worker", 4)
    worker_pids = {}

    for i in range(worker_count):
        w_data = spawn_worker(config,i)

        worker_pids[w_data["w_pid"]] = w_data

        debug_log(f"Spawned Worker{i} PID: {w_data["w_pid"]}")

    while True:
        try:
            pid, status = os.wait()
            if pid in worker_pids:
                w_id = worker_pids[pid]['w_id']

                debug_log(f"Worker{w_id} PID: {pid} exited. Respawning...")

                del worker_pids[pid]

                w_data = spawn_worker(config,w_id)
                worker_pids[w_data["w_pid"]] = w_data

                debug_log(f"Respawned Worker{w_id} PID: {w_data["w_pid"]}")
        except ChildProcessError:
            # No child processes left — shouldn't happen in normal cases
            break
        except KeyboardInterrupt:
            print("Shutting down master and workers...")

            for pid,w_data in worker_pids.items():
                debug_log(f"Stopping Worker{w_data['w_id']} PID: {pid}")
                os.kill(pid, signal.SIGTERM)
            break

    print(f"Mini Nginx Stopped...")
