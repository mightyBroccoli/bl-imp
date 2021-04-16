## bl-imp - the JabberSpam bl(acklist) imp(orter)

### precursor
Please be warned that at this point the JabberSpam blacklist is the only list that will be utilized. It is planed to
open up the tool to also import other lists in the future.

### install
The tool can be installed easily via that Python package installer (pip). After that the local wrapper `/usr/bin/bl-imp`
can be called to use the module.
```bash
pip install bl-imp
```

### `bl-imp` usage
```
usage: bl-imp [-h] [-o OUTFILE] [-dr]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        set path to output file
  -dr, --dry-run        perform a dry run
```

#### without any arguments
Running `bl-imp` without any arguments, cause the tool to update the local cache and the corresponding etag file. After
that the tool will exit with the exit code `2` followed by the help message to stderr.

```bash
no outfile assigned
```

#### dry run
Running `bl-imp` with `-dr` or `--dry-run` as argument will cause the tool to only output the aggregated yaml file to
stdout. Except the local etag and cache file no file is written to disk.

```bash
$ /usr/bin/bl-imp --dry-run
outfile selected: None
acl:
  spamblacklist:
    server:
      - "a-server.tld"
      - "b-server.tld"
```

#### --outfile /path/out.yml
Adding the `outfile` argument while omitting the dry run argument runs the tools  silently while doing its thing.

### ejabberd configuration
To fully utilize the tool some configuration changes are required.
It is required that the tool is the only one editing the defined yml file. It is required because any local change not
present in the remote list will be overwritten automatically.
Furthermore it is necessary for the file to be separate from the "main" ejabberd configuration file e.g `ejabberd.yml`.
To further protect the integrity of your config the `allow_only` sections defines only `acl` rules.

#### ejabberd acl config
```yaml
## ACL section
include_config_file:
  "/etc/ejabberd/blacklist.yml":   <-- the path is completely user configurable
    allow_only:                    <-- these two lines are optional but recommended
      - acl                         └─ to prevent potentially malicious acls to not incluse anthing but ACL rules

## Access Rules
access_rules:
  s2s_access:
    - deny: spamblacklist
    - allow
```

### automation
The tools is meant to be deployed in an automatic fashion. It is build to operate silently without interrupting the
ejabberd server.

For example the script could be run every day at 00:01 to automatically add and remove affected servers from the local
blacklist.

```cron
# jabber blacklist update

# the outfile here is configured with the shortflag -o instead of the long form
1 0 * * * /usr/bin/bl-imp -o  /etc/ejabberd/config/blacklist.yml
```
