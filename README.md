# Web Profile — Ansible + Docker Deployment Demo

> **Target audience:** Undergraduate students learning DevOps / cloud computing.

This project demonstrates how to **automate the full deployment** of a web
application using **Ansible** and **Docker**. Ansible acts as the automation
engine — it installs Docker, builds the container image, starts two app
containers, and launches an **Nginx load balancer**, all without any manual
Docker commands.

---

## What You Will Learn

- How Ansible **inventories**, **playbooks**, and **roles** work together
- How to manage Docker containers declaratively with Ansible
- How Nginx performs **round-robin load balancing** across containers
- The principle of **idempotency** (re-running a playbook is safe)

---

## Architecture

```
        Your Browser
             │
             ▼  port 9000  (public entry point)
   ┌─────────────────────────┐
   │   Nginx Load Balancer   │  container: webprofile_lb  (nginx:alpine)
   │   /lb-health  → 200 OK  │
   └──────────┬──────────────┘
              │  round-robin (alternates every request)
       ┌──────┴──────┐
       ▼             ▼
  port 9001      port 9002
┌──────────┐  ┌──────────┐
│  App 1   │  │  App 2   │  image: webprofile:latest
│ Python   │  │ Python   │  (built from app/Dockerfile)
│ server   │  │ server   │
└──────────┘  └──────────┘

All three containers share Docker network: webprofile_net
App containers expose /server-info so you can see which one served you.
```

---

## Project Structure

```
profile/
├── app/
│   ├── index.html          ← Single-page web profile (HTML + CSS + JS)
│   ├── style.css           ← Stylesheet
│   ├── server.py           ← Python HTTP server (serves static files +
│   │                          /server-info JSON endpoint)
│   └── Dockerfile          ← Builds the webprofile:latest image
│
├── nginx/
│   └── nginx.conf          ← Nginx round-robin load balancer config
│
├── ansible/
│   ├── inventory.ini       ← Defines which host(s) to deploy to
│   ├── playbook.yml        ← MAIN ENTRY POINT — run this to deploy
│   └── roles/
│       ├── docker_install/ ← Role 1: Install Docker (skips if present)
│       ├── build_app/      ← Role 2: Copy source & build Docker image
│       ├── deploy_app/     ← Role 3: Start webprofile_1 & webprofile_2
│       └── deploy_lb/      ← Role 4: Start Nginx load balancer
│
├── docker-compose.yml      ← Quick-start alternative (no Ansible needed)
└── README.md               ← This file
```

---

## Deploying with Ansible (Step-by-Step)

This is the main demo. Follow these steps exactly.

### Step 1 — Install Prerequisites

Run these once on the machine that will run Ansible (the **control node**):

```bash
# Install Ansible
pip3 install ansible

# Install the community.docker Ansible collection
ansible-galaxy collection install community.docker

# Install the Python Docker SDK (used by the community.docker modules)
pip3 install docker
```

Verify installation:

```bash
ansible --version
# ansible [core 2.x.x] ...
```

---

### Step 2 — Review the Inventory

Open `ansible/inventory.ini`. It tells Ansible **where** to deploy.

```ini
[webservers]
# Deploy to THIS local machine:
localhost ansible_connection=local

# Deploy to a REMOTE server (uncomment and edit):
# 192.168.1.100  ansible_user=ubuntu  ansible_ssh_private_key_file=~/.ssh/id_rsa
```

- Use `localhost` to deploy on the same machine (no SSH needed).
- Replace with a real IP to deploy to a cloud VM or lab server.

---

### Step 3 — Review the Playbook

Open `ansible/playbook.yml`. This is what Ansible will execute.

```
playbook.yml
  └── hosts: webservers          (from inventory.ini)
  └── vars:
  │     lb_port:   9000          (public load balancer port)
  │     app1_port: 9001          (direct access container 1)
  │     app2_port: 9002          (direct access container 2)
  └── roles:
        1. docker_install   →  Ensure Docker is installed
        2. build_app        →  Build the webprofile Docker image
        3. deploy_app       →  Start webprofile_1 and webprofile_2
        4. deploy_lb        →  Start the Nginx load balancer
```

---

### Step 4 — Teardown (start fresh for the demo)

If the stack is already running, clean it up first so the demo shows a
complete deployment from scratch:

```bash
docker stop webprofile_1 webprofile_2 webprofile_lb
docker rm   webprofile_1 webprofile_2 webprofile_lb
docker network rm webprofile_net
docker rmi  webprofile:latest
```

---

### Step 5 — Optional: Dry Run

Before making any changes, do a dry run to see what Ansible *would* do:

```bash
cd /home/widhi/profile/ansible
ansible-playbook -i inventory.ini playbook.yml --check
```

Tasks marked `changed` will be executed for real in the next step.
Tasks marked `ok` are already in the desired state.

---

### Step 6 — Run the Playbook

```bash
cd /home/widhi/profile/ansible
ansible-playbook -i inventory.ini playbook.yml
```

Expected output (each task shows its status):

```
PLAY [Deploy Web Profile Stack] ***********************************************

TASK [Gathering Facts] ********************************************************
ok: [localhost]

TASK [docker_install : Check if Docker is already installed] ******************
ok: [localhost]

TASK [docker_install : Install prerequisite packages] *************************
skipping: [localhost]          ← skipped because Docker is already installed

TASK [docker_install : Ensure Docker service is started and enabled] **********
ok: [localhost]

TASK [docker_install : Install Docker SDK for Python] *************************
skipping: [localhost]          ← skipped because docker SDK already present

TASK [build_app : Create remote directory for app source] *********************
ok: [localhost]

TASK [build_app : Copy application source files to target host] ***************
ok: [localhost]

TASK [build_app : Build Docker image from source] *****************************
changed: [localhost]           ← image (re)built from Dockerfile

TASK [build_app : Show build result] ******************************************
ok: [localhost] => { "msg": "Image build status: Rebuilt" }

TASK [deploy_app : Create a dedicated Docker network for the stack] ***********
changed: [localhost]           ← created: webprofile_net

TASK [deploy_app : Start web container 1 (webprofile_1)] *********************
changed: [localhost]           ← started on :9001

TASK [deploy_app : Start web container 2 (webprofile_2)] *********************
changed: [localhost]           ← started on :9002

TASK [deploy_app : Verify containers are running] *****************************
ok: [localhost] => (item=webprofile_1)
ok: [localhost] => (item=webprofile_2)

TASK [deploy_app : Print container status] ************************************
ok: [localhost] => "msg": "webprofile_1 → running"
ok: [localhost] => "msg": "webprofile_2 → running"

TASK [deploy_lb : Create remote directory for Nginx config] *******************
changed: [localhost]

TASK [deploy_lb : Copy Nginx config to target host] **************************
changed: [localhost]           ← nginx.conf copied to /opt/webprofile/nginx/

TASK [deploy_lb : Start Nginx load balancer container] ************************
changed: [localhost]           ← started on :9000

TASK [deploy_lb : Wait for load balancer to be healthy] ***********************
ok: [localhost]                ← /lb-health returned 200 OK

TASK [deploy_lb : Print load balancer status] *********************************
ok: [localhost] => { "msg": "Load balancer is UP at http://localhost:9000" }

TASK [Deployment Summary] *****************************************************
ok: [localhost] => {
    "msg": [
        "════════════════════════════════════════",
        " Deployment Complete!",
        "════════════════════════════════════════",
        " Load Balancer : http://localhost:9000",
        " Container 1   : http://localhost:9001",
        " Container 2   : http://localhost:9002",
        "════════════════════════════════════════"
    ]
}

PLAY RECAP ********************************************************************
localhost : ok=20  changed=6  unreachable=0  failed=0  skipped=4  rescued=0
```

> **Key:** `ok` = already correct, `changed` = Ansible made it happen,
> `skipped` = condition not met (e.g. Docker was already installed),
> `failed` = error (should be 0).

---

### Step 7 — Access the Application

| URL | Description |
|-----|-------------|
| `http://localhost:9000` | **Load balancer** — main entry point |
| `http://localhost:9001` | Direct to **Container 1** (debug) |
| `http://localhost:9002` | Direct to **Container 2** (debug) |
| `http://localhost:9000/lb-health` | Nginx health check endpoint |

---

## Step 8 — Verify Load Balancing

Open `http://localhost:9000` in your browser. Each refresh is served by a
different container. The "Served by" banner on the page updates automatically.

Or use the terminal:

```bash
# Run 4 times — watch the container name alternate
for i in 1 2 3 4; do
  curl -s http://localhost:9000/server-info | python3 -m json.tool
done
```

Actual output from this server:

```
Request 1 → { "container": "webprofile_1", "hostname": "39d60f869b9b", "ip": "172.20.0.2", "port": 8080 }
Request 2 → { "container": "webprofile_2", "hostname": "16447433ee20", "ip": "172.20.0.3", "port": 8080 }
Request 3 → { "container": "webprofile_1", "hostname": "39d60f869b9b", "ip": "172.20.0.2", "port": 8080 }
Request 4 → { "container": "webprofile_2", "hostname": "16447433ee20", "ip": "172.20.0.3", "port": 8080 }
```

Nginx uses **round-robin** by default — requests alternate 1 → 2 → 1 → 2.
The hostnames are the Docker container IDs (short hash).

---

## Alternative: Docker Compose (no Ansible)

If you just want to spin up the stack quickly without going through Ansible:

```bash
cd /home/widhi/profile

# Build images and start all three containers
docker compose up --build -d

# Check status
docker ps

# Stop and remove everything
docker compose down
```

> Use Ansible for the real demo — Docker Compose is just a shortcut for quick testing.

---

## Teardown (Ansible-deployed stack)

```bash
# Stop and remove all three containers
docker stop webprofile_1 webprofile_2 webprofile_lb
docker rm   webprofile_1 webprofile_2 webprofile_lb

# Remove the shared Docker network
docker network rm webprofile_net

# Remove the built image
docker rmi webprofile:latest

# Confirm everything is gone
docker ps -a | grep webprofile    # should return nothing
```

---

## Key File Explanations

### `ansible/inventory.ini`
Tells Ansible which machines to manage. `ansible_connection=local` means
no SSH — Ansible runs directly on this machine.

### `ansible/playbook.yml`
The entry point. Declares the target hosts, port variables, and the list
of roles to run in order.

### `ansible/roles/docker_install/tasks/main.yml`
Checks if Docker is already installed. If not, installs it via apt.
Always ensures the Docker service is running. Installs the Python Docker SDK.

### `ansible/roles/build_app/tasks/main.yml`
Copies `app/` source files to `/opt/webprofile/app/` on the target host,
then builds the `webprofile:latest` Docker image from the Dockerfile.

### `ansible/roles/deploy_app/tasks/main.yml`
Creates the `webprofile_net` Docker network (if not present), then starts
`webprofile_1` on port 9001 and `webprofile_2` on port 9002. Verifies
both containers reach `running` state.

### `ansible/roles/deploy_lb/tasks/main.yml`
Copies `nginx/nginx.conf` to the host and starts the `nginx:alpine`
container on port 9000. Polls `/lb-health` until Nginx responds 200 OK.

### `nginx/nginx.conf`
Defines an `upstream` block with both app containers as backends.
Nginx distributes incoming requests with round-robin automatically.

### `app/server.py`
A minimal Python HTTP server that serves the static files and exposes
two extra endpoints:
- `GET /server-info` — returns JSON with container name, hostname, IP
- `GET /health` — returns `OK` (for health checks)

---

## Ansible Concepts Demonstrated

| Concept | Description | Where |
|---------|-------------|-------|
| **Inventory** | Define target hosts | `inventory.ini` |
| **Playbook** | Orchestrate the full deployment | `playbook.yml` |
| **Roles** | Reusable, modular task groups | `roles/*/tasks/main.yml` |
| **Variables** | Port numbers defined once, used everywhere | `vars:` in playbook |
| **Modules** | `apt`, `pip`, `service`, `copy`, `file`, `uri`, `debug` | Throughout roles |
| **Community collection** | `community.docker.*` for Docker management | deploy_app, deploy_lb |
| **Conditionals** | `when: docker_check.rc != 0` skips install if present | docker_install |
| **Register + loop** | Capture and print container status | deploy_app |
| **Post tasks** | Summary printed after all roles finish | playbook.yml |
| **Idempotency** | Safe to re-run; won't duplicate containers | All roles |

---

## Exercises for Students

1. **Scale up** — Add `webprofile_3` in `roles/deploy_app/tasks/main.yml`
   and add `server webprofile_3:8080;` in `nginx/nginx.conf`.

2. **Remote deploy** — Edit `inventory.ini`, uncomment the remote server
   line, fill in the IP and SSH key, then re-run the playbook. Ansible
   will SSH in and deploy everything automatically.

3. **Rolling update** — Change the profile name in `index.html`, then run:
   ```bash
   ansible-playbook -i inventory.ini playbook.yml
   ```
   Ansible rebuilds the image and restarts containers — the LB stays up.

4. **Health checks** — Add to `app/Dockerfile`:
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/health || exit 1
   ```

5. **Idempotency test** — Run the playbook twice in a row. The second run
   should show all `ok` and zero `changed` — Ansible only acts when
   something is not in the desired state.

6. **Verbose mode** — Add `-v`, `-vv`, or `-vvv` to see increasingly
   detailed output:
   ```bash
   ansible-playbook -i inventory.ini playbook.yml -v
   ```

---

*Built for educational purposes — DevOps / Cloud Computing course.*
