# Building and running

## Initial setup

use the provided `shell.nix` and start vscode inside the shell

```
gradle genSources # Generate minecraft sources
gradle vscode # set up for vscode (if you use a different IDE refer to the fabric docs)
```

## Building
```
grade build # after each code change (if minecraft is restarted, otherwise hot code replace can be used for small changes)
```


# If things break

`gradle cleanloom`
