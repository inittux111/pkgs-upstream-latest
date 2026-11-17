# pkgs-upstream-latest

Specs for a personal COPR repo that follows the latest upstream releases.
See README.md for the `pkg` workflow (add, build, update, remove), and
copr.conf for the COPR project and chroots. Each package lives in
`packages/<name>/`, with `<name>.spec` and a `package.conf` that gives its
`UPSTREAM` (and optionally `EXCLUDE_CHROOTS`).

## Choosing how to package

Check the upstream's release assets for a prebuilt package first, and
repackage it by default:

1. an `.rpm` (e.g. heroic, teams-for-linux, youtube-music)
2. otherwise a `.deb` (e.g. signal-desktop)
3. otherwise build from source

Build from source anyway when there is a good reason, and say why in the
spec. For example:

- The upstream RPM targets one Fedora release (e.g. `.fc44`) and links against
  system libraries (GTK, libadwaita, libvirt, webkitgtk), so it would break
  on other chroots in copr.conf. This is why virt-manager-nextgen and
  whatsup-desktop build from source.
- No RPM or DEB is published.

Repackaged apps (usually Electron) go under `/opt/<name>`. Exclude the
bundled libraries from automatic provides and requires, and list the runtime
dependencies by hand (see teams-for-linux.spec).

## Not Fedora

This repo only feeds a personal COPR, and getting into Fedora is not a goal.
Don't refactor specs to follow Fedora packaging guidelines (vendored crates,
`%cargo_*` macros, dropping `/opt` repackaging, bundled-license audits)
unless asked. A spec is good when it builds and works on COPR.
