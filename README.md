# pkgs-upstream-latest

Packages built from the latest upstream releases, hosted in my personal [COPR repo](https://copr.fedorainfracloud.org/coprs/inittux0101/pkgs-upstream-latest).

Each package is a spec in `packages/<name>/`; `pkg` adds, updates and
builds them.

## Setup

```bash
sudo dnf install copr-cli rpmdevtools rpm-build jq gh
# Log in at COPR (Fedora account) and save your API token
# from https://copr.fedorainfracloud.org/api/ to ~/.config/copr
./pkg setup        # create the COPR project (settings in copr.conf)
```

## Adding a package

```bash
./pkg add <name>                      # if Fedora has it: uses Fedora's spec
./pkg add <name> github:owner/repo    # otherwise: give the upstream,
./pkg add <name> gitlab:group/project #   on GitHub or GitLab
./pkg add <name> https://gitlab.com/group/project   # a URL works too
./pkg build <name>                    # start its build on COPR
git add packages/<name> && git commit -m "Add <name>" && git push
```

For example `./pkg add starship github:starship/starship` or
`./pkg add btrfs-assistant gitlab:btrfs-assistant/btrfs-assistant`.
`add` adds the package to this repo, writing a spec for the latest upstream
release under `packages/<name>/`; `build` then starts its build on COPR.
Fedora's specs and Rust and Go projects usually build as-is; for other
projects `add` lists `TODO`s to fill in (dependencies and installed files)
before you run `build`.

If a build fails, fix `packages/<name>/<name>.spec` and run `build` again.

## Other commands

```bash
./pkg build --all            # build every package in packages/ in COPR
./pkg list                   # spec version vs latest upstream release
./pkg update [<name>]        # bump specs to the latest upstream release,
                             # commit and push them (--no-push, --no-commit)
./pkg bump <name> <version>  # set a spec to a specific version
./pkg srpm <name>            # only build the SRPM locally, to test a spec
./pkg status                 # recent COPR builds
./pkg --help                 # usage summary of every command
```

## Removing a package

```bash
./pkg remove <name>   # asks first, then deletes it from COPR and packages/
git commit -m "Remove <name>" && git push
```

Deleting it from COPR removes all its builds; computers that installed it
keep it, but get no more updates (uninstall with `sudo dnf remove <name>`).

## Automatic updates

A GitHub Action (`.github/workflows/update.yml`) runs `update` and `build`
every 6 hours, so pushed packages follow upstream on their own. It also
runs when you push a change to `packages/`, so bumps you made with
`./pkg update` get built right away, and it rebuilds packages whose latest
COPR build failed. Another one
(`test.yml`) checks daily that updating and the latest COPR builds still
work. GitHub mails you when either fails.

The Action needs your COPR API token as the `COPR_CONFIG` secret. Renew it
when the token expires (every 180 days):

```bash
gh secret set COPR_CONFIG < ~/.config/copr
```
