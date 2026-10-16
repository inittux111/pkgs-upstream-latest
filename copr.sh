#!/usr/bin/env bash
# Build the packages in packages/ in a Fedora COPR project.
# Run with --help for usage; see README.md for details.

set -euo pipefail
# Let errors (die) inside $(...) stop the script too.
shopt -s inherit_errexit

SELF="$(readlink -f "${BASH_SOURCE[0]}")"
ROOT_DIR="$(dirname "$SELF")"
BUILD_DIR="$ROOT_DIR/build"
# shellcheck source=copr.conf
source "$ROOT_DIR/copr.conf"

log()  { printf '\e[1;34m==>\e[0m %s\n' "$*" >&2; }
warn() { printf '\e[1;33mWarning:\e[0m %s\n' "$*" >&2; }
die()  { printf '\e[1;31mError:\e[0m %s\n' "$*" >&2; exit 1; }

usage() {
    local me="${0##*/}"
    cat <<EOF
Usage: $me <command> [args]

Add a package:   $me new <package> [<upstream>]
                 $me build <package>
                 git add packages/<package>, commit and push

Commands:
  new <pkg> [<upstream>]  create packages/<pkg>/ (from Fedora's spec, else a
                          new one). <upstream> is where releases come from:
                            github:owner/repo     e.g. github:starship/starship
                            gitlab:group/project  e.g. gitlab:btrfs-assistant/btrfs-assistant
                            or a github.com / gitlab.com URL
  build <pkg>             build the package in COPR (also to rebuild it)
  list [<pkg>]            spec version vs latest upstream release (-l)
  update [<pkg>]          bump specs to the latest upstream release (-u)
  bump <pkg> <version>    set a spec to a specific version
  srpm <pkg>              only build the SRPM locally, to test a spec
  status                  recent COPR builds
  setup                   create the COPR project or apply copr.conf to it

Settings: copr.conf (project: $COPR_PROJECT). See README.md for details.
EOF
}

need() {
    local cmd pkg
    for cmd in "$@"; do
        case "$cmd" in
            copr-cli)  pkg=copr-cli ;;
            spectool|rpmdev-bumpspec) pkg=rpmdevtools ;;
            rpmbuild|rpmspec) pkg=rpm-build ;;
            *) pkg="$cmd" ;;
        esac
        command -v "$cmd" >/dev/null || die "'$cmd' not found. Install it with: sudo dnf install $pkg"
    done
}

package_names() {
    local d
    for d in "$ROOT_DIR"/packages/*/; do
        [[ -e "$d" ]] && basename "$d"
    done
}

spec_of() {
    local spec="$ROOT_DIR/packages/$1/$1.spec"
    [[ -n "$1" ]] || die "No package given. Packages: $(package_names | xargs)"
    [[ -f "$spec" ]] || die "Unknown package '$1' (no $spec). Packages: $(package_names | xargs)
Add it with: ${0##*/} new $1 [github:owner/repo | gitlab:group/project]"
    printf '%s\n' "$spec"
}

spec_version() { rpmspec -q --srpm --qf '%{VERSION}\n' "$1" 2>/dev/null | head -n1; }

copr_owner() {
    local owner
    owner="$(copr-cli whoami 2>/dev/null)" \
        || die "copr-cli is not logged in. Save your API token from https://copr.fedorainfracloud.org/api/ to ~/.config/copr"
    printf '%s\n' "$owner"
}

# github_api <path>: GET https://api.github.com/<path>, authenticated when
# GITHUB_TOKEN is set (avoids the low anonymous rate limit, e.g. in CI)
github_api() {
    local auth=()
    [[ -z "${GITHUB_TOKEN:-}" ]] || auth=(-H "Authorization: Bearer $GITHUB_TOKEN")
    curl -fsSL "${auth[@]}" "https://api.github.com/$1"
}

# latest_release <forge:owner/repo>: newest release tag as upstream names it
# (e.g. 3.0.0 or v3.0.0)
latest_release() {
    local forge="${1%%:*}" repo="${1#*:}" tag=""
    case "$forge" in
        github)
            tag="$(github_api "repos/$repo/releases/latest" 2>/dev/null \
                | jq -r '.tag_name // empty')" || true
            [[ -n "$tag" ]] || tag="$(github_api "repos/$repo/tags?per_page=100" \
                | jq -r '.[].name' | grep -E '^v?[0-9]+(\.[0-9]+)*$' | sort -V | tail -n1)"
            ;;
        gitlab)
            local id="${repo//\//%2F}"
            tag="$(curl -fsSL "https://gitlab.com/api/v4/projects/$id/releases/permalink/latest" 2>/dev/null \
                | jq -r '.tag_name // empty')" || true
            [[ -n "$tag" ]] || tag="$(curl -fsSL "https://gitlab.com/api/v4/projects/$id/repository/tags?per_page=100" \
                | jq -r '.[].name' | grep -E '^v?[0-9]+(\.[0-9]+)*$' | sort -V | tail -n1)"
            ;;
        *) die "Unknown upstream forge in '$1' (use github: or gitlab:)." ;;
    esac
    [[ -n "$tag" ]] || return 1
    printf '%s\n' "$tag"
}

# latest_tag <forge:owner/repo>: newest release version (tag without a leading v)
latest_tag() {
    local tag
    tag="$(latest_release "$1")" || return 1
    printf '%s\n' "${tag#v}"
}

# upstream_from_url <url | forge:path>: print github:owner/repo or gitlab:group/project
upstream_from_url() {
    local url="${1%/}"
    url="${url%.git}"
    case "$url" in
        github:?*/?*|gitlab:?*/?*) printf '%s\n' "$url" ;;
        http*://github.com/?*/?*)
            url="${url#*://github.com/}"
            printf 'github:%s\n' "$(cut -d/ -f1-2 <<<"$url")"
            ;;
        http*://gitlab.com/?*/?*)
            url="${url#*://gitlab.com/}"
            printf 'gitlab:%s\n' "${url%%/-/*}"
            ;;
        *) return 1 ;;
    esac
}

upstream_of() {
    (
        UPSTREAM=""
        # shellcheck source=/dev/null
        [[ -f "$ROOT_DIR/packages/$1/package.conf" ]] && source "$ROOT_DIR/packages/$1/package.conf"
        printf '%s\n' "$UPSTREAM"
    )
}

cmd_setup() {
    need copr-cli curl
    local owner chroot args=()
    owner="$(copr_owner)"
    for chroot in $CHROOTS; do args+=(--chroot "$chroot"); done
    args+=(--enable-net "$COPR_ENABLE_NET")

    if curl -fsS -o /dev/null \
        "https://copr.fedorainfracloud.org/api_3/project?ownername=$owner&projectname=$COPR_PROJECT" 2>/dev/null; then
        log "Project $owner/$COPR_PROJECT exists; updating its chroots to: $CHROOTS (network: $COPR_ENABLE_NET)"
        copr-cli modify "$COPR_PROJECT" "${args[@]}"
    else
        log "Creating COPR project $owner/$COPR_PROJECT"
        copr-cli create "$COPR_PROJECT" "${args[@]}" \
            --description "$COPR_DESCRIPTION" \
            --instructions "sudo dnf copr enable $owner/$COPR_PROJECT"
    fi
    log "Project page: https://copr.fedorainfracloud.org/coprs/$owner/$COPR_PROJECT/"
}

# upstream_latest <package>: print the latest upstream release. Returns 2 if
# the package has no UPSTREAM (skipped), 1 if the lookup failed.
upstream_latest() {
    local upstream latest
    upstream="$(upstream_of "$1")"
    if [[ -z "$upstream" ]]; then
        warn "$1: no UPSTREAM in packages/$1/package.conf, skipping."
        return 2
    fi
    if ! latest="$(latest_tag "$upstream")"; then
        warn "$1: could not determine the latest release of $upstream."
        return 1
    fi
    printf '%s\n' "$latest"
}

# is_newer <have> <latest>: true if <latest> is a higher version than <have>
is_newer() {
    [[ "$1" != "$2" && "$(printf '%s\n%s\n' "$1" "$2" | sort -V | tail -n1)" == "$2" ]]
}

cmd_list() {
    need rpmspec curl jq
    local name names have latest status lrc rc=0
    names="${1:-$(package_names)}"
    printf '  %-20s %-12s %-12s %s\n' PACKAGE SPEC LATEST STATUS
    for name in $names; do
        have="$(spec_version "$(spec_of "$name")")"
        lrc=0
        latest="$(upstream_latest "$name" 2>/dev/null)" || lrc=$?
        if (( lrc == 2 )); then
            latest="-" status="no UPSTREAM in packages/$name/package.conf"
        elif (( lrc != 0 )); then
            latest="?" status="could not look up $(upstream_of "$name")"
            rc=1
        elif is_newer "$have" "$latest"; then
            status="update available: ${0##*/} update $name"
        else
            status="up to date"
        fi
        printf '  %-20s %-12s %-12s %s\n' "$name" "$have" "$latest" "$status"
    done
    return "$rc"
}

cmd_update() {
    need rpmspec curl jq rpmdev-bumpspec
    local name names have latest updated=0 rc=0
    names="${1:-$(package_names)}"
    for name in $names; do
        have="$(spec_version "$(spec_of "$name")")"
        latest="$(upstream_latest "$name")" || { (( $? == 2 )) || rc=1; continue; }
        if is_newer "$have" "$latest"; then
            log "$name: updating $have -> $latest"
            cmd_bump "$name" "$latest"
            updated=$((updated + 1))
        else
            log "$name: up to date ($have)"
        fi
    done
    (( updated > 0 )) || log "No spec changes."
    return "$rc"
}

cmd_bump() {
    need rpmdev-bumpspec rpmspec
    local spec ver="${2:-}"
    spec="$(spec_of "${1:-}")"
    [[ -n "$ver" ]] || die "Usage: ${0##*/} bump <package> <version>"
    rpmdev-bumpspec -n "$ver" -c "Update to $ver" "$spec"
    log "Spec now at $(rpmspec -q --srpm --qf '%{VERSION}-%{RELEASE}\n' "$spec" | head -n1)."
    log "Review with 'git diff', then build with: ${0##*/} build $1"
}

# fedora_import <package> <dir> <clonedir>: copy Fedora's spec and the local
# sources/patches it uses into <dir>. Returns 1 if Fedora has no such package.
fedora_import() {
    local name="$1" dir="$2" clone="$3" spec="$2/$1.spec" ver entry src
    curl -fsS -o /dev/null "https://src.fedoraproject.org/api/0/rpms/$name" 2>/dev/null || return 1
    log "Importing $name from Fedora (https://src.fedoraproject.org/rpms/$name)"
    GIT_TERMINAL_PROMPT=0 git clone -q --depth 1 "https://src.fedoraproject.org/rpms/$name.git" "$clone" \
        || return 1
    [[ -f "$clone/$name.spec" ]] || { warn "Fedora's $name is retired (no spec)."; return 1; }
    cp "$clone/$name.spec" "$spec"

    # Swap rpmautospec's %autorelease/%autochangelog for a plain Release and
    # changelog, which build without rpmautospec and work with bump/update.
    sed -i -E 's/^(Release:[[:space:]]*)%\{?autorelease\}?.*/\11%{?dist}/' "$spec"
    if grep -q '^%autochangelog' "$spec"; then
        ver="$(spec_version "$spec")"
        entry="* $(LC_ALL=C date '+%a %b %d %Y') $(rpmdev-packager) - $ver-1"$'\n'"- Import from Fedora"
        E="$entry" awk '/^%autochangelog/ { print ENVIRON["E"]; next } 1' "$spec" >"$spec.new"
        mv "$spec.new" "$spec"
    fi

    # Sources and patches without a URL live next to the spec in dist-git.
    while read -r src; do
        src="${src#*: }"
        [[ "$src" == *://* ]] && continue
        if [[ -f "$clone/${src##*/}" ]]; then
            cp "$clone/${src##*/}" "$dir/"
        else
            warn "$name: '${src##*/}' is not in Fedora's git (probably in its lookaside cache); add it to packages/$name/ yourself."
        fi
    done < <(spectool -l "$spec" 2>/dev/null)
}

# write_template <package> <upstream> <dir>: write a starting spec for the
# latest release of <upstream>, guessing the build system from its files.
# Rust and Go projects get a complete spec: cargo/go download the
# dependencies at build time (needs COPR_ENABLE_NET=on) and every program
# they build is installed into /usr/bin.
write_template() {
    local name="$1" upstream="$2" dir="$3"
    local forge="${upstream%%:*}" repo="${upstream#*:}" project="${upstream##*/}"
    local tag version prefix api url source meta summary description license files dirs
    local br="" build="# TODO: build the software" install="# TODO: install into %{buildroot}" b
    local header="# Spec template written by \`copr.sh new\`: fill in the TODOs."
    local deps="# TODO: BuildRequires/Requires for the libraries it uses"
    local installed=$'# TODO: list the installed files; a failed build lists them under\n# "Installed (but unpackaged) file(s) found"'
    local tree

    tag="$(latest_release "$upstream")" || die "Could not find a release of $upstream."
    version="${tag#v}"
    prefix="${tag%"$version"}"
    [[ "$version" =~ ^[0-9][0-9A-Za-z.+~_]*$ ]] \
        || die "The latest tag of $upstream ('$tag') is not a version rpm can use."

    case "$forge" in
        github)
            api="repos/$repo"
            url="https://github.com/$repo"
            source="%{url}/archive/$prefix%{version}/%{name}-%{version}.tar.gz"
            meta="$(github_api "$api")"
            license="$(jq -r '.license.spdx_id // empty | select(. != "NOASSERTION")' <<<"$meta")"
            tree="$(github_api "$api/contents?ref=$tag")"
            files="$(jq -r '.[] | select(.type == "file") | .name' <<<"$tree")"
            dirs="$(jq -r '.[] | select(.type == "dir") | .name' <<<"$tree")"
            ;;
        gitlab)
            api="https://gitlab.com/api/v4/projects/${repo//\//%2F}"
            url="https://gitlab.com/$repo"
            source="%{url}/-/archive/$prefix%{version}/$project-$prefix%{version}.tar.gz"
            meta="$(curl -fsSL "$api")"
            license=""  # GitLab doesn't report SPDX identifiers
            tree="$(curl -fsSL "$api/repository/tree?ref=$tag&per_page=100")"
            files="$(jq -r '.[] | select(.type == "blob") | .name' <<<"$tree")"
            dirs="$(jq -r '.[] | select(.type == "tree") | .name' <<<"$tree")"
            ;;
        *) die "Unknown upstream forge in '$upstream' (use github: or gitlab:)." ;;
    esac
    description="$(jq -r '.description // empty' <<<"$meta")"
    summary="${description%%$'\n'*}"
    summary="${summary%.}"

    # Install every program in <dir> (not libraries) into /usr/bin.
    local install_bins='mkdir -p %{buildroot}%{_bindir}
find @DIR@ -maxdepth 1 -type f -perm -u+x ! -name "*.so" \
    -exec install -pm 0755 -t %{buildroot}%{_bindir} {} +'

    if grep -qx Cargo.toml <<<"$files"; then
        local locked=""
        grep -qx Cargo.lock <<<"$files" && locked=" --locked"
        br="cargo rust gcc"
        build=$'export RUSTFLAGS="%{build_rustflags}"\ncargo build --release'"$locked"
        install="${install_bins//@DIR@/target/release}"
        header="# Spec written by \`copr.sh new\`: cargo downloads the crates at build time
# (COPR_ENABLE_NET=on in copr.conf)."
        deps="" installed="%{_bindir}/*"
    elif grep -qx go.mod <<<"$files"; then
        # The program is main.go at the top, else one or more under cmd/.
        local pkgs="."
        grep -qx main.go <<<"$files" || ! grep -qx cmd <<<"$dirs" || pkgs="./cmd/..."
        br="golang gcc"
        build="mkdir -p _bin
go build -buildmode=pie -trimpath -ldflags \"-B gobuildid\" -o _bin/ $pkgs"
        install="${install_bins//@DIR@/_bin}"
        header="# Spec written by \`copr.sh new\`: go downloads the modules at build time
# (COPR_ENABLE_NET=on in copr.conf).

# -trimpath leaves no source paths for a debugsource package.
%global debug_package %{nil}"
        deps="" installed="%{_bindir}/*"
    elif grep -qx CMakeLists.txt <<<"$files"; then
        br="cmake gcc-c++" build=$'%cmake\n%cmake_build' install="%cmake_install"
    elif grep -qx meson.build <<<"$files"; then
        br="meson gcc" build=$'%meson\n%meson_build' install="%meson_install"
    elif grep -qx configure <<<"$files"; then
        br="gcc make" build=$'%configure\n%make_build' install="%make_install"
    elif grep -qx configure.ac <<<"$files"; then
        br="autoconf automake libtool gcc make" build=$'autoreconf -fi\n%configure\n%make_build' install="%make_install"
    elif grep -qx Makefile <<<"$files"; then
        br="gcc make" build="%make_build" install="%make_install PREFIX=%{_prefix}"
    elif grep -qxE 'pyproject.toml|setup.py' <<<"$files"; then
        build="# TODO: Python project; pyp2spec (dnf install pyp2spec) can generate a full spec"
    fi

    {
        cat <<EOF
$header

Name:           $name
Version:        $version
Release:        1%{?dist}
Summary:        ${summary:-TODO: one-line summary}

License:        ${license:-TODO}
URL:            $url
Source0:        $source

EOF
        for b in $br; do printf 'BuildRequires:  %s\n' "$b"; done
        [[ -z "$deps" ]] || printf '%s\n' "$deps"
        printf '\n'
        printf '%%description\n%s\n\n\n' "$(fold -s -w 76 <<<"${description:-TODO: description}" | sed 's/ *$//')"
        printf '%%prep\n@AUTOSETUP@\n\n%%build\n%s\n\n%%install\n%s\n\n\n%%files\n' "$build" "$install"
        sed -nE 's/^(LICEN[CS]E|COPYING)/%license &/p' <<<"$files"
        sed -n 's/^README/%doc &/p' <<<"$files"
        cat <<EOF
$installed

%changelog
* $(LC_ALL=C date '+%a %b %d %Y') $(rpmdev-packager) - $version-1
- Initial package
EOF
    } >"$dir/$name.spec"
}

cmd_new() {
    need curl jq git rpmspec spectool rpmdev-bumpspec rpmdev-packager
    local name="${1:-}" upstream="" dir tmp spec url have latest src top setup ver rep='%{version}'
    [[ -n "$name" && "$name" != */* ]] \
        || die "Usage: ${0##*/} new <package> [github:owner/repo | gitlab:group/project | URL]"
    dir="$ROOT_DIR/packages/$name"
    [[ ! -e "$dir" ]] || die "packages/$name already exists."
    if [[ -n "${2:-}" ]]; then
        upstream="$(upstream_from_url "$2")" \
            || die "Unknown upstream '$2' (use github:owner/repo, gitlab:group/project or a github.com/gitlab.com URL)."
    fi

    # Assemble the package in a temporary directory, so a failure leaves nothing behind.
    tmp="$(mktemp -d)"
    # shellcheck disable=SC2064  # expand $tmp now: it is local
    trap "rm -rf '$tmp'" EXIT
    mkdir "$tmp/pkg"
    spec="$tmp/pkg/$name.spec"

    if fedora_import "$name" "$tmp/pkg" "$tmp/fedora"; then
        if [[ -z "$upstream" ]]; then
            for url in "$(rpmspec -q --srpm --qf '%{URL}\n' "$spec" 2>/dev/null | head -n1)" \
                       "$(spectool -l -s 0 "$spec" 2>/dev/null | sed 's/^[^:]*: //')"; do
                upstream="$(upstream_from_url "$url")" && break
            done
            [[ -n "$upstream" ]] || die "Fedora's $name spec doesn't point to GitHub or GitLab. Pass the upstream: ${0##*/} new $name github:owner/repo"
        fi
    else
        [[ -n "$upstream" ]] || die "$name is not in Fedora. Pass its upstream: ${0##*/} new $name github:owner/repo"
        log "Writing a spec template for $upstream"
        write_template "$name" "$upstream" "$tmp/pkg"
    fi

    cat >"$tmp/pkg/package.conf" <<EOF
# Upstream of this package, used by \`./copr.sh list\` and \`update\` to find new releases.
# shellcheck shell=bash
UPSTREAM="$upstream"
EOF

    latest="$(latest_tag "$upstream")" || die "Could not find the latest release of $upstream."
    have="$(spec_version "$spec")"
    if is_newer "$have" "$latest"; then
        log "Updating $have -> $latest (latest release of $upstream)"
        rpmdev-bumpspec -n "$latest" -c "Update to $latest" "$spec"
    fi

    mkdir -p "$ROOT_DIR/packages"
    mv "$tmp/pkg" "$dir"
    spec="$dir/$name.spec"
    log "Created packages/$name ($(spec_version "$spec"), upstream $upstream)"

    # Templates: unpack into whatever top directory the source archive uses.
    if grep -qx '@AUTOSETUP@' "$spec"; then
        log "Downloading sources for $name"
        spectool -g -C "$BUILD_DIR/$name" "$spec" >&2
        src="$(spectool -l -s 0 "$spec" | sed 's|.*/||')"
        top="$(tar -tf "$BUILD_DIR/$name/$src" | sed -n '1s|/.*||p')"
        ver="$(spec_version "$spec")"
        setup="%autosetup -p1"
        [[ "$top" == "$name-$ver" ]] || setup+=" -n ${top//"$ver"/"$rep"}"
        sed -i "s|^@AUTOSETUP@\$|$setup|" "$spec"
    fi

    if ( cmd_srpm "$name" >/dev/null ); then
        log "Sources download and the SRPM builds."
    else
        warn "Building the SRPM failed; fix packages/$name/$name.spec and retry with: ${0##*/} srpm $name"
    fi
    if grep -q 'TODO' "$spec"; then
        log "Next: fill in the TODOs in packages/$name/$name.spec, then: ${0##*/} build $name"
    else
        log "Next: review packages/$name, then: ${0##*/} build $name"
    fi
}

cmd_srpm() {
    need spectool rpmbuild
    local name="${1:-}" spec out
    spec="$(spec_of "$name")"
    out="$BUILD_DIR/$name"
    mkdir -p "$out"
    rm -f "$out"/*.src.rpm

    log "Downloading sources for $name"
    spectool -g -C "$out" "$spec" >&2
    # Local patches/extra sources next to the spec.
    find "$(dirname "$spec")" -maxdepth 1 -type f ! -name '*.spec' ! -name package.conf \
        -exec cp -t "$out" {} +

    log "Building SRPM"
    rpmbuild -bs "$spec" --define "_sourcedir $out" --define "_srcrpmdir $out" >&2
    ls "$out"/*.src.rpm
}

cmd_build() {
    need copr-cli
    local name="${1:-}" srpm
    shift || true
    spec_of "$name" >/dev/null
    srpm="$(cmd_srpm "$name" | tail -n1)"
    log "Submitting $(basename "$srpm") to COPR project $COPR_PROJECT"
    copr-cli build "$COPR_PROJECT" "$srpm" "$@"
}

cmd_status() {
    need copr-cli
    copr-cli list-builds "$COPR_PROJECT" | head -n 20
}

main() {
    local cmd="${1:-}"
    shift || true
    case "$cmd" in
        setup)   cmd_setup "$@" ;;
        new|add) cmd_new "$@" ;;
        list|-l) cmd_list "$@" ;;
        update|--update|-u) cmd_update "$@" ;;
        bump)    cmd_bump "$@" ;;
        srpm)    cmd_srpm "$@" ;;
        build)   cmd_build "$@" ;;
        status)  cmd_status "$@" ;;
        -h|--help|help|"") usage ;;
        *) usage >&2; die "Unknown command '$cmd'." ;;
    esac
}

main "$@"
