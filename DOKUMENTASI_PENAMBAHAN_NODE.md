# Dokumentasi: Penambahan Node Webserver Baru (Multi-Node Architecture)



**Tanggal:** 16 Maret 2026  
**Tujuan:** Melakukan skalabilitas horizontal dengan menambah 1 node webserver baru ke arsitektur yang sudah ada




**Anggota:** 
1. Muhammad Farid Ramdhani  - 235150207111018
2. Muhammad Fatih Satrio    - 235150200111018
---

## 📋 Daftar Isi

1. [Konsep Arsitektur](#konsep-arsitektur)
2. [Langkah-Langkah Teoritis](#langkah-langkah-teoritis)
3. [Implementasi Teknis yang Dilakukan](#implementasi-teknis-yang-dilakukan)
4. [File-File yang Diubah](#file-file-yang-diubah)
5. [Cara Deployment](#cara-deployment)
6. [Verifikasi dan Testing](#verifikasi-dan-testing)

---

## <a name="konsep-arsitektur"></a>1. Konsep Arsitektur

### Arsitektur SEBELUM (Single Node)

```
┌─────────────────────────────────────────────────┐
│           LOCALHOST (Node 1)                    │
├─────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐   │
│  │  Load Balancer (Nginx)                  │   │
│  │  Port: 9000                             │   │
│  └──────────────┬──────────────────────────┘   │
│                 │                              │
│       ┌─────────┴──────────┐                  │
│       ▼                    ▼                  │
│  ┌─────────┐         ┌─────────┐             │
│  │ App 1   │         │ App 2   │             │
│  │ 9001    │         │ 9002    │             │
│  └─────────┘         └─────────┘             │
│                                              │
│  Docker Network: webprofile_net              │
└─────────────────────────────────────────────────┘
```

### Arsitektur SESUDAH (Multi-Node)

```
┌──────────────────────────────────────┐
│   LOCALHOST (Node 1)                 │
├──────────────────────────────────────┤
│  ┌──────────────────────────────┐   │
│  │ Load Balancer (Nginx)        │   │
│  │ Port: 9000                   │   │
│  │                              │   │
│  │ Upstream Pool:               │   │
│  │ - webprofile_1:8080 ┐        │   │
│  │ - webprofile_2:8080 ├──┐    │   │
│  │ - webprofile_3:8080 ─────┐  │   │
│  └──────────────────────────────┘   │
│       ▼              ▼              │
│  ┌────────┐    ┌────────┐           │
│  │ App 1  │    │ App 2  │           │
│  │:9001   │    │:9002   │           │
│  └────────┘    └────────┘           │
│                                    │
│ Docker Network: webprofile_net     │
└──────────────────────────────────────┘
                  │
                  ↓ (Remote Connection)
┌──────────────────────────────────────┐
│   WEBSERVER2 (Node 2)                │
├──────────────────────────────────────┤
│  ▼                                   │
│  ┌────────────────────────────────┐  │
│  │ App 3 Container                │  │
│  │ Port: 9001 (internal)          │  │
│  │ Port: 9003 (external/host)     │  │
│  └────────────────────────────────┘  │
│                                      │
│ Docker Network: webprofile_net       │
└──────────────────────────────────────┘
```

**Perubahan Utama:**

- Dari 2 container → 3 container
- Dari 1 node → 2 node (localhost + webserver2)
- Load balancer tetap di localhost, mengarahkan traffic ke 3 backend
- Container ke-3 berjalan di node terpisah

---

## <a name="langkah-langkah-teoritis"></a>2. Langkah-Langkah Teoritis Penambahan Node

### Fase 1: Planning & Design

**Tujuan:** Merancang arsitektur multi-node sebelum implementasi

1. **Tentukan jumlah node** → 2 node (localhost + 1 remote)
2. **Alokasi container per node**
   - Node 1 (localhost): App 1, App 2, Load Balancer
   - Node 2 (webserver2): App 3
3. **Planning port mapping:**
   - Load Balancer: 9000
   - App 1: 9001 (localhost)
   - App 2: 9002 (localhost)
   - App 3: 9003 (external), 9001 (internal)
4. **Definisikan network configuration**
   - Docker network yang sama untuk semua (webprofile_net)
   - Connectivity rules

### Fase 2: Infrastructure Setup

**Tujuan:** Menyiapkan infrastruktur server

1. **Provision Node 2**
   - Buat/sediakan server kedua (cloud, on-premise, atau VM)
   - Install OS (Ubuntu/CentOS)
   - Install Docker & Docker Compose
   - Setup SSH key untuk Ansible

2. **Setup SSH Access**
   - Generate SSH key pair (jika belum ada)
   - Copy public key ke server kedua
   - Test koneksi SSH

3. **Verify Network Connectivity**
   - Ping dari localhost ke Node 2
   - Test SSH connection

### Fase 3: Configuration Management (Ansible)

**Tujuan:** Mengotomasi deployment dengan Ansible

1. **Update Inventory**
   - Tambah node baru ke `inventory.ini`
   - Define SSH credentials dan connection method

2. **Modifikasi Playbook**
   - Update architecture diagram
   - Tambah variabel untuk port baru
   - Tambah info container baru di post-tasks

3. **Update Roles**
   - **build_app:** Build image di SEMUA node
   - **deploy_app:** Deploy container dengan kondisi (localhost vs webserver2)
   - **deploy_lb:** Deploy load balancer hanya ke localhost

4. **Create Dynamic Configuration**
   - Buat Jinja2 template untuk nginx.conf
   - Auto-inject backend IP dari inventory

### Fase 4: Validation & Testing

**Tujuan:** Memastikan deployment berhasil

1. **Deployment Test**

   ```bash
   ansible-playbook -i inventory.ini playbook.yml -K
   ```

2. **Container Status Check**

   ```bash
   docker ps
   ```

3. **Load Balancer Health Check**

   ```bash
   curl http://localhost:9000/lb-health
   ```

4. **Test Routing**
   ```bash
   curl http://localhost:9000/server-info     # Via LB
   curl http://localhost:9001/server-info     # Direct App 1
   curl http://localhost:9002/server-info     # Direct App 2
   curl http://localhost:9003/server-info     # Direct App 3
   ```

### Fase 5: Documentation & Handover

**Tujuan:** Dokumentasi untuk maintenance

1. Update README dengan arsitektur baru
2. Document scaling procedure
3. Create runbook untuk troubleshooting
4. Commit ke version control

---

## <a name="implementasi-teknis-yang-dilakukan"></a>3. Implementasi Teknis yang Dilakukan

### Perubahan 1: Inventory Update (`ansible/inventory.ini`)

**SEBELUM:**

```ini
[webservers]
# ── Option A: Deploy to this local machine ────────
localhost ansible_connection=local

# ── Option B: Deploy to a remote server (uncomment and edit)
# 192.168.1.100  ansible_user=ubuntu  ansible_ssh_private_key_file=~/.ssh/id_rsa
```

**SESUDAH:**

```ini
[webservers]
# ── Node 1: Local machine (Load Balancer + App 1 & 2)
localhost ansible_connection=local

# ── Node 2: Localhost secondary (App 3)
# Untuk testing: run 3 containers pada mesin yang sama
webserver2 ansible_connection=local
```

**Penjelasan:**

- Menambah `webserver2` sebagai host baru
- `ansible_connection=local` → Node 2 juga menggunakan localhost (untuk testing)
- Di production, ini akan diganti dengan `ansible_host=IP_SERVER` + SSH credentials

---

### Perubahan 2: Playbook Update (`ansible/playbook.yml`)

#### 2.1 Architecture Diagram

**Tujuan:** Documenting arsitektur multi-node

**SEBELUM:**

```yaml
#    Internet  ──►  [Load Balancer :9000]
#                         │
#              ┌──────────┴──────────┐
#              ▼                     ▼
#      [webprofile_1 :9001]   [webprofile_2 :9002]
```

**SESUDAH:**

```yaml
#    Internet  ──►  [Load Balancer localhost:9000]
#                         │
#              ┌──────────┼──────────┐
#              ▼          ▼          ▼
#    [webprofile_1    [webprofile_2 [webprofile_3
#     localhost:9001]  localhost:9002] webserver2:9003]
```

#### 2.2 Variables Update

**Tujuan:** Menambah port mappings untuk container ketiga

```yaml
vars:
  lb_port: 9000 # Load Balancer
  app1_port: 9001 # Container 1
  app2_port: 9002 # Container 2
  app3_port: 9003 # Container 3 (NEW)
```

#### 2.3 Post-Tasks Update

**Tujuan:** Show all 3 containers dalam deployment summary

```yaml
post_tasks:
  - name: Deployment Summary
    debug:
      msg:
        - " Load Balancer : http://{{ inventory_hostname }}:{{ lb_port }}"
        - " Container 1   : http://{{ inventory_hostname }}:{{ app1_port }}"
        - " Container 2   : http://{{ inventory_hostname }}:{{ app2_port }}"
        - " Container 3   : http://{{ hostvars['webserver2'].get('ansible_host', 'localhost') }}:{{ app3_port }}"
```

**Penjelasan `.get('ansible_host', 'localhost')`:**

- Cek apakah `webserver2` punya attribute `ansible_host`
- Jika ada (remote server) → gunakan IP tersebut
- Jika tidak ada (localhost) → fallback ke 'localhost'

---

### Perubahan 3: Deploy App Role (`ansible/roles/deploy_app/tasks/main.yml`)

#### 3.1 Tambah Container 3

```yaml
- name: Start web container 3 (webprofile_3) - on webserver2 only
  community.docker.docker_container:
    name: webprofile_3
    image: webprofile:latest
    state: started
    restart_policy: always
    networks:
      - name: webprofile_net
    ports:
      - "9003:8080" # Port 9003 di host → 8080 di container
    env:
      CONTAINER_NAME: "webprofile_3"
      PORT: "8080"
  when: inventory_hostname != 'localhost' # Hanya jalankan di Node 2
```

**Penjelasan:**

- **Port Mapping:** `9003:8080` untuk external access ke App 3
- **Kondisi `when:`** → Container 3 hanya dijalankan di `webserver2` (tidak di localhost)
- Ini mencegah duplikasi/conflict container di localhost

#### 3.2 Dynamic Container Verification

```yaml
- name: Verify containers are running
  community.docker.docker_container_info:
    name: "{{ item }}"
  loop: "{{ container_list }}"
  register: container_info
  vars:
    container_list: |
      {%- if inventory_hostname == 'localhost' -%}
        ['webprofile_1', 'webprofile_2']
      {%- else -%}
        ['webprofile_3']
      {%- endif -%}
```

**Penjelasan:**

- Menggunakan Jinja2 conditional
- Jika node adalah `localhost` → verify container 1 & 2
- Jika node adalah `webserver2` → verify container 3 saja
- Flexible & scalable untuk node tambahan di masa depan

---

### Perubahan 4: Deploy LB Role (`ansible/roles/deploy_lb/`)

#### 4.1 Load Balancer Container (hanya di localhost)

```yaml
- name: Start Nginx load balancer container (localhost only)
  community.docker.docker_container: ...
  when: inventory_hostname == 'localhost'
```

**Penjelasan:** Load balancer hanya boleh satu (di Node 1), jadi ditambah kondisi

#### 4.2 Template Created: `nginx.conf.j2`

**File baru:** `ansible/roles/deploy_lb/templates/nginx.conf.j2`

```nginx
upstream webprofile_cluster {
    server webprofile_1:8080;      # Container 1 (localhost)
    server webprofile_2:8080;      # Container 2 (localhost)
{%- if groups['webservers'] | length > 1 %}
    {%- if 'ansible_host' in hostvars[groups['webservers'][1]] %}
    # Remote webserver2 accessed via IP:port
    server {{ hostvars[groups['webservers'][1]]['ansible_host'] }}:9001;
    {%- else %}
    # Local webserver2 (same machine) - accessible via docker network
    server webprofile_3:8080;
    {%- endif %}
{%- endif %}
}
```

**Penjelasan Template:**

- **Line 1-2:** Backend untuk container di localhost (accessible via docker network name)
- **Line 3-11:** Conditional block - jika ada lebih dari 1 node
  - Jika Node 2 punya `ansible_host` → gunakan IP + port eksternal
  - Jika Node 2 di localhost → gunakan docker network name

**Keuntungan Jinja2 Template:**

- Dynamic configuration berdasarkan inventory
- Support both localhost testing dan production multi-server deployment
- Tidak perlu manual edit nginx.conf

---

### Perubahan 5: Build App Role (`ansible/roles/build_app/tasks/main.yml`)

**SEBELUM:**

```yaml
- name: Show build result
  debug:
    msg: "Image build status: {{ build_result.changed | ternary('Rebuilt', 'No change') }}"
```

**SESUDAH:**

```yaml
- name: Show build result
  debug:
    msg: "{{ inventory_hostname }} → Image build status: {{ build_result.changed | ternary('Rebuilt', 'No change') }}"
```

**Penjelasan:** Tambah `{{ inventory_hostname }}` untuk clarify image dibangun di node mana

---

### Perubahan 6: Docker Compose Reference (`docker-compose.yml`)

**Tujuan:** Dokumentasi untuk local development

Menambah commented-out container 3:

```yaml
# ── Web App Container 3 (Reference for Ansible deployment) ────────
# This container is deployed via Ansible to webserver2 (remote node)
# For local testing, uncomment and customize the host/port:
# webprofile_3:
#   build:
#     context: ./app
#     dockerfile: Dockerfile
#   container_name: webprofile_3
#   restart: always
#   environment:
#     - CONTAINER_NAME=webprofile_3
#     - PORT=8080
#   ports:
#     - "9003:8080"
#   networks:
#     - webprofile_net
```

---

## <a name="file-file-yang-diubah"></a>4. File-File yang Diubah

| File                                | Perubahan                                                      | Alasan                       |
| ----------------------------------- | -------------------------------------------------------------- | ---------------------------- |
| `inventory.ini`                     | +Tambah `webserver2` node                                      | Mendefinisikan node baru     |
| `playbook.yml`                      | +Architecture diagram, +var app3_port, +post-tasks container 3 | Update diagram & info output |
| `deploy_app/tasks/main.yml`         | +Container 3 task, +Dynamic verification                       | Deploy container ke node 2   |
| `deploy_lb/tasks/main.yml`          | +`when: localhost` condition                                   | LB hanya di 1 lokasi         |
| `deploy_lb/templates/nginx.conf.j2` | **[FILE BARU]**                                                | Dynamic upstream config      |
| `build_app/tasks/main.yml`          | +Show hostname in output                                       | Clarity identifikasi node    |
| `docker-compose.yml`                | +Container 3 reference                                         | Development reference        |

---

## <a name="cara-deployment"></a>5. Cara Deployment

### Prerequisites

```bash
# 1. Pastikan Docker sudah install
docker --version

# 2. Pastikan Python & Ansible di localhost
ansible --version

# 3. Test connectivity ke inventory
cd ansible
ansible all -i inventory.ini -m ping
```

### Deployment Steps

**Step 1:** Deploy semua

```bash
cd ansible
ansible-playbook -i inventory.ini playbook.yml -K
```

**Output yang diharapkan:**

- ✅ Tasks di 2 node selesai (localhost + webserver2)
- ✅ Image built di kedua node
- ✅ 3 containers running (1, 2 di localhost; 3 di webserver2)
- ✅ Load balancer UP di localhost

**Step 2:** Verify status containers

```bash
# Semua containers
docker ps

# Output:
# CONTAINER ID   STATUS    PORTS              NAMES
# ...            running   0.0.0.0:9000->80   webprofile_lb
# ...            running   0.0.0.0:9001->8080 webprofile_1
# ...            running   0.0.0.0:9002->8080 webprofile_2
# ...            running   0.0.0.0:9003->8080 webprofile_3
```

---

## <a name="verifikasi-dan-testing"></a>6. Verifikasi dan Testing

### Test 6.1: Load Balancer Health

```bash
curl http://localhost:9000/lb-health
# Output: Load balancer is healthy
```

### Test 6.2: Round-Robin via Load Balancer

```bash
for i in {1..6}; do
  curl http://localhost:9000/server-info | jq '.container'
done

# Output (alternating between 3 containers):
# "webprofile_1"
# "webprofile_2"
# "webprofile_3"
# "webprofile_1"
# "webprofile_2"
# "webprofile_3"
```

### Test 6.3: Direct Container Access

```bash
# Container 1
curl http://localhost:9001/server-info | jq .container
# Output: "webprofile_1"

# Container 2
curl http://localhost:9002/server-info | jq .container
# Output: "webprofile_2"

# Container 3
curl http://localhost:9003/server-info | jq .container
# Output: "webprofile_3"
```

### Test 6.4: Network Connectivity

```bash
# Test DNS resolution dalam Docker network
docker exec webprofile_1 ping webprofile_2
docker exec webprofile_1 ping webprofile_3
```

---

## 📊 Comparison Table: Before vs After

| Aspek                   | BEFORE           | AFTER                       |
| ----------------------- | ---------------- | --------------------------- |
| **Jumlah Node**         | 1 (localhost)    | 2 (localhost + webserver2)  |
| **Jumlah Container**    | 2                | 3                           |
| **Load Balancer**       | ✅ (1 LB)        | ✅ (1 LB)                   |
| **Port Mapping**        | 9000, 9001, 9002 | 9000, 9001, 9002, 9003      |
| **Inventory Entries**   | 1                | 2                           |
| **Playbook Complexity** | Simple           | Medium (conditional logic)  |
| **Scalability**         | Limited          | Good (ready for more nodes) |
| **High Availability**   | No               | Better (distributed)        |

---

## 🎯 Keuntungan Multi-Node Architecture

1. **High Availability**
   - Jika Node 1 down, Node 2 masih serve traffic
   - Service tetap berjalan walaupun 1 node fail

2. **Load Distribution**
   - Traffic terdistribusi ke 3 backend
   - Mengurangi beban pada single machine

3. **Scalability**
   - Easy to add more nodes (repeat pattern)
   - Infrastructure siap untuk growth

4. **Resource Optimization**
   - Leverage multiple servers
   - Optimal resource utilization

5. **Maintainability**
   - Update/restart di satu node tidak affect node lain
   - Zero-downtime deployment possible

---

## ⚙️ Future Enhancements

### Untuk Production Deployment:

1. **Ganti localhost dengan Real Server**

   ```ini
   webserver2 ansible_host=192.168.1.100 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa
   ```

2. **Add Health Checks**
   - Container health probes
   - LB health monitoring

3. **Add Logging & Monitoring**
   - ELK Stack atau Prometheus
   - Centralized logging

4. **Add Database Layer**
   - PostgreSQL/MySQL container
   - Persistent volume management

5. **Add Persistent Storage**
   - Docker volumes for state management
   - Backup strategy

6. **Add SSL/TLS**
   - HTTPS untuk load balancer
   - Certificate management

---

## 📝 Kesimpulan

Proses penambahan node webserver baru dari **single-node menjadi multi-node architecture** melibatkan:

1. **Planning** → Design arsitektur multi-node
2. **Infrastructure** → Provision server baru, setup SSH
3. **Configuration** → Update Ansible inventory, roles, templates
4. **Automation** → Create dynamic Jinja2 templates untuk flexibility
5. **Testing** → Verify semua containers running dan load balancer working
6. **Documentation** → Record changes untuk maintenance

Dengan pendekatan Infrastructure-as-Code (Ansible), proses scaling menjadi repeatable, maintainable, dan production-ready.

---

**Untuk Production Deployment:** Update `inventory.ini` dengan IP server real dan SSH credentials, kemudian jalankan playbook yang sama. Arsitektur sudah siap!
