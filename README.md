## Security research tool for auditing Dahua DVRs with default credentials. 📹
- **This tool is intended strictly against systems for which you have explicit, documented permission from the owner!** Unauthorized access to computer systems is illegal in many jurisdictions. By using this software, you agree that you are **solely responsible** for complying with all applicable laws. ⚠️

### Installation 💿
#### 🚀 Run from Source
```
git clone https://github.com/zyg0t/dahua-audit.git
cd dahua-audit
python3 main.py
```
### Usage 🖥️
#### `main.py -b ips.txt -t 200 -s 0`
- **ips.txt** [FILE] > List of IPv4 addresses written in plaintext, in a txt file, each on a separate line:
```
157.240.22.35
185.199.108.153
[...and so on]
```
- **200** [THREADS] > Number of threads, default is 200
- **0** [SPLIT] > Number of entries per XML file, default is 0

### Configuration ⚙️ [*config.py*]
- DEFAULT_THREADS = 200 > **number of threads**
- DEFAULT_TIMEOUT = 3 > **seconds before skipping**
- DEFAULT_PORT = 37777 > **default Dahua port**
- DEFAULT_SPLIT = 0 > **how many lines per XML file (0 does not split)**

### Credits 🫡
**https://github.com/S0Ulle33/asleep_scanner** for the foundation of this codebase and providing incredibly helpful insight into the proprietary protocol used ♥️
