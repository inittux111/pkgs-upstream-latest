# Built from source: upstream publishes no RPM or DEB (only a Linux tarball,
# a Flatpak and Windows/macOS installers).
# cargo downloads the crates at build time (COPR_ENABLE_NET=on in copr.conf).

%global app_id org.squidowl.halloy

Name:           halloy
Version:        2026.10
Release:        1%{?dist}
Summary:        IRC application written in Rust

License:        GPL-3.0-or-later
URL:            https://github.com/squidowl/halloy
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  desktop-file-utils

# winit and wgpu dlopen these, so rpm doesn't pick them up on its own.
Requires:       libxkbcommon
Requires:       libwayland-client
Requires:       libX11
Requires:       libXcursor
Requires:       libXi
Requires:       libXrandr
Requires:       libglvnd-egl
Requires:       vulkan-loader
Requires:       hicolor-icon-theme

%description
Halloy is an open-source IRC client written in Rust, with the iced GUI
library.


%prep
%autosetup -p1

%build
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
    assets/linux/%{app_id}.desktop
mkdir -p %{buildroot}%{_datadir}/icons
cp -r assets/linux/icons/hicolor %{buildroot}%{_datadir}/icons/
install -Dpm 0644 -t %{buildroot}%{_metainfodir} assets/linux/%{app_id}.appdata.xml


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/icons/hicolor/*/apps/%{app_id}.png
%{_metainfodir}/%{app_id}.appdata.xml

%changelog
* Tue Nov 17 2026 Maarten <github@feedmebits.nl> - 2026.10-1
- Initial package
