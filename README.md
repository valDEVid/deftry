# Welcome to the Deftry Tool
<br></br>

## Docs

### Install
Start cloning trhe repository in your workfolder

```
git clone https://github.com/valDEVid/deftry
```

<br></br>
Once you get it, `cd` to the directory

And run it
```
python3 deftry.py
```

<br></br>
### Usage

You can actually see the help pannel by launch `-h` flag
```
python3 deftry.py -h
```
`--help` will work also 

<br></br>
URL is the obligated flag (`-u`), but you have a few more to run the script 

```
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

### Clarifications

You can already do this with **wfuzz**, but this was made to improve up my python tools knowledges and actually is a more specified tool, so, it will go directly to the point.
Thanks for read.

---

#### Near updates

Actually trying to make the tool abe to work with threads with customizable ammount.

