import re
import os
import config
from pathlib import Path

def parse_target_file(filepath):
    hosts = []

    if not Path(filepath).exists():
        config.logger.error(f"File {filepath} not found.")
        return []

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            ip_match = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
            if not ip_match:
                continue
            ip = ip_match[0]
            port_match = re.search(r'tcp (\d+)', line)
            if port_match:
                port = port_match.group(1)
            elif ':' in line:
                parts = line.split(':')
                if len(parts) >= 2 and parts[1].isdigit():
                    port = parts[1]
                else:
                    port = config.DEFAULT_PORT
            else:
                port = config.DEFAULT_PORT

            hosts.append((ip, int(port)))

    return list(set(hosts))

def save_to_csv(results, filename='dahua.csv', split_size=0):
    if not results:
        return

    with open(filename, 'a', encoding='utf-8') as f:
        for res in results:
            line = f"{res['ip']},{res['port']},{res['login']},{res['password']},{res['model']}\n"
            f.write(line)

    config.logger.info(f"Saved results to {filename}")

    deduplicate_csv(filename)
    csv_to_xml(filename, filename.replace('.csv', '.xml'), split_size=split_size)


def deduplicate_csv(filename='dahua.csv'):
    if not Path(filename).exists():
        config.logger.warning(f"{filename} not found for deduplication.")
        return

    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    duplicates_removed = len(lines) - len(unique_lines)

    if duplicates_removed > 0:
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(unique_lines)

        config.logger.info("-" * 40)
        config.logger.info(f"Removed {duplicates_removed} duplicate entries.")


def csv_to_xml(csv_filename='dahua.csv', xml_filename='dahua.xml', split_size=0):
    if not Path(csv_filename).exists():
        config.logger.error(f"{csv_filename} not found for XML conversion.")
        return

    devices = []

    with open(csv_filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(',')
            if len(parts) < 4:
                continue

            ip = parts[0].strip()
            port = parts[1].strip()
            user = parts[2].strip()
            password = parts[3].strip()
            title = f"{ip}_{user}:{password}"

            devices.append(
                f'    <Device title="{title}" ip="{ip}" port="{port}" user="{user}" password="{password}"/>\n'
            )

    if split_size <= 0:
        file_chunks = [devices]
    else:
        file_chunks = [devices[i:i + split_size] for i in range(0, len(devices), split_size)]

    # Write XML files
    for idx, chunk in enumerate(file_chunks, start=1):
        if len(file_chunks) == 1:
            out_file = xml_filename
        else:
            base, ext = os.path.splitext(xml_filename)
            out_file = f"{base}{idx}{ext}"

        with open(out_file, 'w', encoding='utf-8') as f:
            f.write("<Organization>\n")
            f.write('  <Department name="root">\n')
            for device in chunk:
                f.write(device)
            f.write("  </Department>\n")
            f.write("</Organization>\n")

        config.logger.info(f"Converted {len(chunk)} entries to {out_file}")
