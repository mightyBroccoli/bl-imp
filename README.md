## Blacklist import script

### installation
Python 3 virtual environment
```bash
# Debian
apt install python-virtualenv

# Arch
pacman -S python-virtualenv

# create a venv folder inside the cloned repository
mkdir venv
virtualenv -p python3 venv/

source ./venv/bin/activate
pip install -r requirements.txt
```

### usage main.py
```
usage: main.py [-h] [-o OUTFILE] [-dr]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        set path to output file
  -dr, --dry-run        perform a dry run
```

#### without any arguments
Running `main.py` without any arguments, will cause the tool to update the local cache and the corresponding `.etag` 
file. After that the script will output the following error followed by the help message to stderr, before exiting with error code `2` 

```bash
no outfile assigned
...
```

#### dry run
If `main.py` is executed with `-dr` or `--dry-run` as argument the output would look like this. The script will check 
the blacklist repository and output everything to stdout without touching any system file besides the local `.etag` file.
```bash
$ /path/blacklist_import: python main.py --dr
outfile selected: None
acl:
  spamblacklist:
    server:
      - "a-server.tld"
      - "b-server.tld"
```

#### --outfile /path/
Run without the `--dry-run` argument and a valid outfile, the script will return nothing and do its thing.

##### *ejabberd reload_config*
The ejabberd instance will be reloaded automatically, but only if changes in the `outfile` occurred.

## configuration
### ejabberd
To use this script properly, you need to add this line to the `ACL` section of your ejabberd instance. Furthermore a 
separate `yml` file is necessary. To further protect the integrity of your config the `allow_only` sections defines only `acl` rules.
```yaml
  "/etc/ejabberd/blacklist.yml":
    allow_only:
      - acl
```

### script itself 
The script is meant to be used in an automatic fashion.

For example the script could be executed every day at 00:01 to automatically add and remove affected servers from the
 blacklist file.

```cron
# jabber blacklist update

# with virtualenv enabled
1 0 * * * /path/blacklist_import/venv/bin/python /path/blacklist_import/main.py -o  /etc/ejabberd/config/blacklist.yml

# without virtualenv
1 0 * * * python3 /path/blacklist_import/main.py -o  /etc/ejabberd/config/blacklist.yml
```
