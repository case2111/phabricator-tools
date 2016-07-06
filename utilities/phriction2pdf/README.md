phriction2pdf
-------------
Convert a phriction page to a pdf

```
make token='your-conduit-token' slug='relative/path/to/wiki' host='http://phab/host/url'
```

alternatively set an environment variable PHAB_API_TOKEN

```
make slug='relative/path/to/wiki'
```

* The 'download' target requires the token and slug

# Syntax

## Links

For links use this approach
```
[name](http://example.com)
```

something like the following would require a converter...
```
[[ http://example.com | name ]]
```
