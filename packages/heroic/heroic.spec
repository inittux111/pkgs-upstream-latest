# Repackaged from Heroic's official RPM; the Electron app is bundled in
# /opt/Heroic. The upstream RPM's scriptlets are not carried over: its
# /usr/bin link is created here, chrome-sandbox stays 0755 (Fedora has user
# namespaces), and the AppArmor profile is not needed on Fedora.

%global debug_package %{nil}
%global __strip /bin/true
# Don't export or require the libraries and helper binaries Heroic bundles;
# the runtime dependencies are listed by hand, as in the upstream RPM.
%global __provides_exclude_from ^/opt/Heroic/.*$
%global __requires_exclude_from ^/opt/Heroic/.*$

Name:           heroic
Version:        2.22.4
Release:        1%{?dist}
Summary:        A games launcher for GOG, Amazon and Epic Games

License:        GPL-3.0-only
URL:            https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher
Source0:        %{url}/releases/download/v%{version}/Heroic-%{version}-linux-x86_64.rpm
ExclusiveArch:  x86_64

BuildRequires:  cpio
BuildRequires:  desktop-file-utils

Requires:       at-spi2-core
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       libnotify
Requires:       libuuid
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       nss
Requires:       xdg-utils

%description
Heroic is an open source games launcher for GOG, Epic Games and Amazon
Games, with support for running Windows games through Wine and Proton.


%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idm --quiet

%build

%install
cp -a opt usr %{buildroot}/
chmod 0755 %{buildroot}/opt/Heroic/chrome-sandbox
# Upstream points the desktop file at /opt; use the /usr/bin link instead.
sed -i 's|^Exec=/opt/Heroic/heroic |Exec=heroic |' \
    %{buildroot}%{_datadir}/applications/heroic.desktop
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/Heroic/heroic %{buildroot}%{_bindir}/heroic

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/heroic.desktop


%files
/opt/Heroic/
%{_bindir}/heroic
%{_datadir}/applications/heroic.desktop
%{_datadir}/icons/hicolor/*/apps/heroic.png

%changelog
* Tue Nov 17 2026 Maarten <github@feedmebits.nl> - 2.22.4-1
- Initial package, repackaged from the official RPM
