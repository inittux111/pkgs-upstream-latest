# Based on upstream's packaging/fedora/whatsup-desktop.spec, but cargo
# downloads the crates at build time (COPR_ENABLE_NET=on in copr.conf)
# instead of using a vendored tarball.

Name:           whatsup-desktop
Version:        1.0.4
Release:        1%{?dist}
Summary:        WhatsApp Web for GNOME

License:        GPL-3.0-or-later
URL:            https://github.com/inittux111/whatsup-desktop
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
# Early builds were packaged as whatsup, a name Fedora already uses for a
# cluster tool; the version bound leaves that one alone.
Obsoletes:      whatsup < 1.1

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(webkitgtk-6.0)
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       libadwaita
Requires:       webkitgtk6.0
Requires:       google-noto-color-emoji-fonts

%description
WhatsUp runs WhatsApp Web in a native GNOME window that stays responsive,
follows your theme and keeps your account data private.

%prep
%autosetup -p1

%build
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
make install DESTDIR=%{buildroot} PREFIX=%{_prefix}

%check
export RUSTFLAGS="%{build_rustflags}"
cargo test --release --locked
desktop-file-validate %{buildroot}%{_datadir}/applications/app.whatsup_desktop.WhatsUp.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/app.whatsup_desktop.WhatsUp.metainfo.xml

%files
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/app.whatsup_desktop.WhatsUp.desktop
%{_datadir}/metainfo/app.whatsup_desktop.WhatsUp.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/app.whatsup_desktop.WhatsUp.svg
%{_datadir}/icons/hicolor/scalable/apps/app.whatsup_desktop.WhatsUp-tray.svg
%{_datadir}/icons/hicolor/scalable/apps/app.whatsup_desktop.WhatsUp-tray-unread.svg
%{_datadir}/icons/hicolor/symbolic/apps/app.whatsup_desktop.WhatsUp-symbolic.svg
%{_datadir}/icons/hicolor/symbolic/apps/app.whatsup_desktop.WhatsUp-unread-symbolic.svg

%changelog
* Sun Oct 18 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.0.4-1
- Update to 1.0.4

* Sun Oct 18 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.0.3-1
- Update to 1.0.3

* Sun Oct 18 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.0.2-1
- Update to 1.0.2

* Sat Oct 17 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.0.1-1
- Update to 1.0.1

* Sat Oct 17 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.0.0-1
- Initial package
