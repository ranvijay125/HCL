import subprocess
import time
import json
import os

NAMESPACE = "matilda"
UNSEAL_FILE = "/home/matildasvc/vault_out"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing: {cmd}")
        print(result.stderr)
        exit(1)
    return result.stdout.strip()

def get_vault_pod():
    cmd = f"kubectl get pods -n {NAMESPACE} -l app.kubernetes.io/name=vault -o json"
    output = run_cmd(cmd)
    pods = json.loads(output)
    return pods["items"][0]["metadata"]["name"]

def delete_pod(pod_name):
    print(f"Restarting pod: {pod_name}")
    run_cmd(f"kubectl delete pod {pod_name} -n {NAMESPACE}")

def wait_for_pod():
    print("Waiting for Vault pod to be ready...")
    while True:
        try:
            pod = get_vault_pod()
            status = run_cmd(f"kubectl get pod {pod} -n {NAMESPACE} -o json")
            pod_json = json.loads(status)
            conditions = pod_json["status"].get("conditions", [])
            for condition in conditions:
                if condition["type"] == "Ready" and condition["status"] == "True":
                    print("Vault pod is ready.")
                    return pod
        except:
            pass
        time.sleep(5)

def read_unseal_keys():
    if not os.path.exists(UNSEAL_FILE):
        print("Unseal file not found!")
        exit(1)

    keys = []
    with open(UNSEAL_FILE, "r") as f:
        for line in f:
            if "Unseal Key" in line or len(line.strip()) > 20:
                keys.append(line.strip().split(":")[-1].strip())

    return keys[:3]  # Typically need first 3 keys

def unseal_vault(pod, keys):
    print("Unsealing Vault...")
    for key in keys:
        cmd = f"kubectl exec -n {NAMESPACE} {pod} -- vault operator unseal {key}"
        run_cmd(cmd)
        time.sleep(2)
    print("Vault unsealed successfully.")

def main():
    pod = get_vault_pod()
    delete_pod(pod)
    pod = wait_for_pod()
    keys = read_unseal_keys()
    unseal_vault(pod, keys)

if __name__ == "__main__":
    main()