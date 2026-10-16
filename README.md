# pkgs-upstream-latest

Build newer upstream releases of packages for Fedora using my [personal COPR repo](https://copr.fedorainfracloud.org/coprs/inittux0101/pkgs-upstream-latest).
Each package is a spec in `packages/<name>/`; `pkg` adds, updates and
builds them.

## Setup

```bash
sudo dnf install copr-cli rpmdevtools rpm-build jq gh
# Save your API token from https://copr.fedorainfracloud.org/api/ to ~/.config/copr
./pkg setup        # create the COPR project (settings in copr.conf)
```

## Adding a package

```bash
./pkg new <name>                      # if Fedora has it: uses Fedora's spec
./pkg new <name> github:owner/repo    # otherwise: give the upstream,
./pkg new <name> gitlab:group/project #   on GitHub or GitLab
./pkg new <name> https://gitlab.com/group/project   # a URL works too
./pkg build <name>                    # build it in COPR
git add packages/<name> && git commit -m "Add <name>" && git push
```

For example `./pkg new starship github:starship/starship` or
`./pkg new btrfs-assistant gitlab:btrfs-assistant/btrfs-assistant`.
`new` writes a spec for the latest upstream release. Fedora's specs and Rust
and Go projects usually build as-is; for other projects `new` lists `TODO`s
to fill in (dependencies and installed files) before you run `build`.

If a build fails, fix `packages/<name>/<name>.spec` and run `build` again.

## Other commands

```bash
./pkg list                   # spec version vs latest upstream release
./pkg update [<name>]        # bump specs to the latest upstream release
./pkg bump <name> <version>  # set a spec to a specific version
./pkg srpm <name>            # only build the SRPM locally, to test a spec
./pkg status                 # recent COPR builds
```

## Automatic updates

A GitHub Action (`.github/workflows/update.yml`) runs `update` and `build`
every day, so pushed packages follow upstream on their own. Another one
(`test.yml`) checks daily that updating and the latest COPR builds still
work. GitHub mails you when either fails.

The Action needs your COPR API token as the `COPR_CONFIG` secret. Renew it
when the token expires (every 180 days):

```bash
gh secret set COPR_CONFIG < ~/.config/copr
```
