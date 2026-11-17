# cargo downloads the crates at build time, and magpie's build script
# downloads nvtop (COPR_ENABLE_NET=on in copr.conf).
#
# Upstream's release tarball leaves out its git submodules, so they are
# separate sources. On each update, set these to the commits the new tag
# pins:
#   magpie:      subprojects/magpie in mission-center
#   app_rummage: platform-linux/crates/app-rummage in magpie (gng)
%global magpie_commit       a5272b3c1d853caa4044b737cf49257bfc4c86f2
%global app_rummage_commit  26b93b8c6f0de6912f0a17022f7ece76bad87612

# The Rust programs are built by cargo through meson without debug info,
# which leaves nothing for a debuginfo package.
%global debug_package %{nil}

%global app_id io.missioncenter.MissionCenter

Name:           mission-center
Version:        1.2.0
Release:        1%{?dist}
Summary:        Monitor your CPU, memory, disk, network and GPU usage

License:        GPL-3.0-or-later
URL:            https://gitlab.com/mission-center-devs/mission-center
Source0:        %{url}/-/archive/v%{version}/mission-center-v%{version}.tar.gz
Source1:        https://gitlab.com/mission-center-devs/gng/-/archive/%{magpie_commit}/gng-%{magpie_commit}.tar.gz
Source2:        https://gitlab.com/mission-center-devs/app-detection/-/archive/%{app_rummage_commit}/app-detection-%{app_rummage_commit}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  cmake
BuildRequires:  patch
BuildRequires:  python3
BuildRequires:  gettext
BuildRequires:  blueprint-compiler
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gtk4) >= 4.22
BuildRequires:  pkgconfig(libadwaita-1) >= 1.9
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libudev)

Requires:       hicolor-icon-theme

%description
Mission Center monitors your overall or per-thread CPU usage, memory, disk,
network and GPU usage, and lists running apps and processes.


%prep
%autosetup -p1 -n mission-center-v%{version}
tar -xf %{SOURCE1} -C subprojects/magpie --strip-components=1
tar -xf %{SOURCE2} -C subprojects/magpie/platform-linux/crates/app-rummage \
    --strip-components=1

%build
# Release build: upstream only passes --release to cargo for this buildtype.
# LTO off: upstream's meson only supports it with clang.
%meson --buildtype=release -Db_lto=false
%meson_build

%install
%meson_install
%find_lang missioncenter

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{app_id}.desktop


%files -f missioncenter.lang
%license COPYING
%doc README.md
%{_bindir}/missioncenter
%{_bindir}/missioncenter-magpie
%{_datadir}/missioncenter/
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/glib-2.0/schemas/%{app_id}.gschema.xml
%{_datadir}/icons/hicolor/*/apps/%{app_id}*.svg
%{_metainfodir}/%{app_id}.metainfo.xml

%changelog
* Tue Nov 17 2026 Maarten <github@feedmebits.nl> - 1.2.0-1
- Initial package
