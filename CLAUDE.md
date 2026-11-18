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
dependencies by hand (see teams-for-linux.spec). Upstream RPMs often leave out
libraries Electron needs (e.g. alsa-lib, mesa-libgbm), and CI only checks that
packages install, not that they start. So install the package in a minimal
Fedora container (`--setopt=install_weak_deps=False`) and check that
`ldd /opt/<name>/<binary> | grep 'not found'` is empty.

## Fedora compatibility

This repo only feeds a personal COPR, and getting into Fedora is not a goal.
Specs don't have to follow Fedora's packaging guidelines fully. Don't refactor
for that unless asked (vendored crates, `%cargo_*` macros, dropping `/opt`
repackaging, bundled-license audits).

What matters is that the packages install cleanly next to Fedora's:

- Don't install files that a Fedora package owns. Keep repackaged apps
  self-contained under `/opt/<name>`, with only a link in `/usr/bin`,
  `.desktop` files and icons outside it.
- Don't export bundled libraries as Provides (or Requires), so dnf never uses
  this repo's packages to satisfy another package's dependency.
- When a package replaces one in Fedora (btrfs-assistant and mangohud do),
  start from Fedora's spec (`./pkg add` does this). Keep the same package
  and subpackage names and the same file layout, and make the
  version-release newer than Fedora's so the COPR build wins.
