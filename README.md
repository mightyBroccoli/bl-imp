## Blacklist import script

### ejabberd config
To use this script properly, a separate `yml` file is necessary, as the script will overwrite the file. To further 
protect the config the `allow_only` sections defines only `acl` rules.
```yaml
  "/etc/ejabberd/blacklist.yml":
    allow_only:
      - acl
```

### script configuration

The script is meant to be used in an automatic fashion.
Arguments:

- -dr , --dry-run : perform a dry run. `blacklist.txt` and `.etag` are written but no yaml file is overwritten.
- -o , --outfile filepath : set path to output file

The dry-run argument will output the file path, if set, in addition to the contents of the yaml file which would have be produced.

### script workflow
1. check if `.etag` file is present
2. HEAD request
	2.1 requests etag and `.etag` are equal
	​	2.1.1 use local `blacklist.txt` file
	2.2 requests etag and `.etag` are _not_ equal
	​	2.2.1 request new `blacklist.txt`
	​	2.2.2 save new `.etag` and `blacklist.txt` file
3. process `blacklist.txt` and parse output file

