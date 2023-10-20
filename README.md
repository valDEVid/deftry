# Welcome to the Deftry Tool
<br></br>

## Docs

### Install
Start cloning the repository in your workfolder

```powershell
git clone https://github.com/valDEVid/deftry
```

<br></br>
Once you get it, `cd` to the directory

And run it
```powershell
python3 deftry.py
```

<br></br>
### Usage

You can actually see the help pannel by launch `-h` flag
```powershell
python3 deftry.py -h
```
`--help` will work also 

<br></br>
URL is the obligated flag (`-u`), but you have a few more to run the script 

```powershell
Default Credentials Checker

options:
  -h, --help            show this help message and exit
  -u [Victim URL]       URL
  -uw [/usr/share/example]
                        Users Wordlist (Must be a list with value per line)
  -pw [/usr/share/example]
                        Password Wordlist (Must be a list with value per line)
  -nc                   No errors checks to compare
```

For now, if the victim web has differents endpoints of the form and the login, for example, a index.php with a login form that is sent to login.php you must set the html as the -u flag and the login as `-p login.php`

```powershell
python3 deftry.py -u https://example.com -p login.php
```

### Clarifications

You can already do this with **wfuzz**, but this was made to improve up my python tools knowledges and actually is a more specified tool, so, it will go directly to the point.
Thanks for read.

---

#### Near updates

* Actually trying to make the tool abe to work with threads with customizable ammount.
* It has an output issue with windows. Only for Linux systems for now

