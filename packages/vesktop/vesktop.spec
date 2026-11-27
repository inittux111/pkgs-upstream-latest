# Repackaged from Vesktop's official RPM; the Electron app is bundled in
# /opt/Vesktop. The upstream RPM's scriptlets are not carried over: its
# /usr/bin link is created here, chrome-sandbox stays 0755 (Fedora has user
# namespaces), and the AppArmor profile is not needed on Fedora.

%global debug_package %{nil}
%global __strip /bin/true
# Don't export or require the libraries and helper binaries Electron bundles;
# the runtime dependencies are listed by hand: the upstream RPM's, plus the
# libraries Electron links against or loads that it leaves out.
%global __provides_exclude_from ^/opt/Vesktop/.*$
%global __requires_exclude_from ^/opt/Vesktop/.*$

Name:           vesktop
Version:        1.7.2
Release:        1%{?dist}
Summary:        Custom Discord desktop app with Vencord built in

License:        GPL-3.0-only
URL:            https://github.com/Vencord/Vesktop
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.x86_64.rpm
ExclusiveArch:  x86_64

BuildRequires:  cpio
BuildRequires:  desktop-file-utils

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       libnotify
Requires:       libuuid
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       nss
# Loaded at run time for audio.
Requires:       pulseaudio-libs
Requires:       xdg-utils

%description
Vesktop is a custom Discord desktop app with Vencord preinstalled, aiming
to give better performance and better Linux support.


%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idm --quiet

%build

%install
cp -a opt usr %{buildroot}/
chmod 0755 %{buildroot}/opt/Vesktop/chrome-sandbox
# Not used on Fedora; the upstream scriptlet only installs it under AppArmor.
rm %{buildroot}/opt/Vesktop/resources/apparmor-profile
# Upstream points the desktop file at /opt; use the /usr/bin link instead.
sed -i 's|^Exec=/opt/Vesktop/vesktop |Exec=vesktop |' \
    %{buildroot}%{_datadir}/applications/vesktop.desktop
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/Vesktop/vesktop %{buildroot}%{_bindir}/vesktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/vesktop.desktop


%files
/opt/Vesktop/
%{_bindir}/vesktop
%{_datadir}/applications/vesktop.desktop
%{_datadir}/icons/hicolor/scalable/apps/vesktop.svg

%changelog
* Fri Nov 27 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.7.2-1
- Update to 1.7.2

* Thu Nov 19 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.7.0-1
- Update to 1.7.0

* Wed Nov 18 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.6.9-2
- Require alsa-lib, mesa-libgbm and pulseaudio-libs, which Electron needs

* Wed Nov 18 2026 Maarten <github@feedmebits.nl> - 1.6.9-1
- Initial package, repackaged from the official RPM
