## 📐 Deployment Environments & Architectural Execution Modes

To ensure cross-platform validation, this framework is engineered to run in two distinct operational modes depending on host kernel privileges:

### 1. Production Mode (`AICS_production.py`)
* **Target Environment:** Enterprise Linux Environments (Ubuntu/Debian Server) with full root/kernel privileges.
* **Core Dependency:** Requires `tshark` binary system packages for raw socket packet ingestion and `scikit-learn` for active algorithmic inference.

### 2. Emulated Simulation Mode (`AICS_simulation.py`)
* **Target Environment:** Restricted POSIX environments / Mobile Sandboxes (Android Termux subsystems).
* **Core Mechanism:** Since mobile mobile kernels restrict raw network interface access (blocking raw packet capturing via `tshark`), I built an in-engine **Traffic Simulator** alongside a **Mock Isolation Forest Layer**. 
* **Objective:** This simulates multi-threaded concurrency, API telemetry logging, and Flask endpoints on the go, allowing for rapid interface and dashboard testing without compiling heavy C-binary wheels on restricted mobile processors.
* 
