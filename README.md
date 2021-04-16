## bl-imp - the JabberSpam bl(acklist) imp(orter)

### precursor
Please be warned that at this point the JabberSpam blacklist is the only list that will be used. It is planed to open up
the tool to also import other lists in the future.

### install
The tool can be installed easily via that Python package Index (pip). After that the local wrapper `/usr/bin/bl-imp`
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
Running `bl-imp` without any arguments, cause the tool to update the local cache and etag file. After that the tool will
exit with the exit code `2` followed by the help message to stderr.

```bash
no outfile assigned
```

#### dry run
Running `bl-imp` with `-dr` or `--dry-run` as argument will cause the tool to only output the aggregated yaml file to
stdout. Except the local etag and cache file no file is written to disk.

```bashinstaller
$ /usr/bin/bl-imp --dry-run
outfile selected: None
acl:
  spamblacklist:
    server:
      - "a-server.tld"
      - "b-server.tld"
```

#### --outfile /path/out.yml
Adding the `outfile` argument while omitting the dry run argument runs the tools silently while doing its thing.

### ejabberd configuration
To fully utilize the tool some configuration changes are required.
Firstly it is necessary that `bl-imp` is the only one editing the defined yml file, because any local change not
present in the remote list will be overwritten automatically. Furthermore it is necessary for the file to be separate
from the "main" ejabberd configuration e.g `ejabberd.yml`. Lastly to protect the integrity of your config files the
`allow_only` argument restricts the external file to only allow for `acl` rules.

#### ejabberd acl config
```yaml
## acl
include_config_file:
  "/etc/ejabberd/blacklist.yml":   # ⟵ the path is completely user configurable
    allow_only:                    # ⟵ the allow_only section is optional but recommended
      - acl

## access rules
access_rules:
  s2s_access:
    - deny: spamblacklist
    - allow
```

### automation
The tool is meant to be used in an automatic fashion. It is build to operate silently without any user interaction.

For example the script could be run every day at 00:01 to automatically add/ remove affected servers from the local
blacklist and reload the configuration if the first task finished successfully.

```cron
# jabber blacklist update

# the outfile here is configured with the shortflag -o instead of the long form
1 0 * * * /usr/bin/bl-imp -o  /etc/ejabberd/config/blacklist.yml && /usr/bin/ejabberdctl reload_config
```
