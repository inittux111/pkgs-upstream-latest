# Repackaged from teams-for-linux's official RPM; the Electron app is bundled
# in /opt/teams-for-linux. The upstream RPM's scriptlets are not carried over:
# its /usr/bin link is created here, chrome-sandbox stays 0755 (Fedora has
# user namespaces), and the AppArmor profile is not needed on Fedora.

%global debug_package %{nil}
%global __strip /bin/true
# Don't export or require the libraries and helper binaries Electron bundles;
# the runtime dependencies are listed by hand, as in the upstream RPM.
%global __provides_exclude_from ^/opt/teams-for-linux/.*$
%global __requires_exclude_from ^/opt/teams-for-linux/.*$

Name:           teams-for-linux
Version:        2.32.0
Release:        1%{?dist}
Summary:        Unofficial Microsoft Teams for Linux client

License:        GPL-3.0-or-later
URL:            https://github.com/IsmaelMartinez/teams-for-linux
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.x86_64.rpm
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
Unofficial Microsoft Teams client for Linux. It wraps the Teams web app in
a standalone Electron application.


%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idm --quiet

%build

%install
cp -a opt usr %{buildroot}/
chmod 0755 %{buildroot}/opt/%{name}/chrome-sandbox
# Not used on Fedora; the upstream scriptlet only installs it under AppArmor.
rm %{buildroot}/opt/%{name}/resources/apparmor-profile
# Upstream points the desktop file at /opt; use the /usr/bin link instead.
sed -i 's|^Exec=/opt/%{name}/%{name} |Exec=%{name} |' \
    %{buildroot}%{_datadir}/applications/%{name}.desktop
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/%{name}/%{name} %{buildroot}%{_bindir}/%{name}

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop


%files
/opt/%{name}/
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
* Tue Nov 17 2026 Maarten <github@feedmebits.nl> - 2.32.0-1
- Initial package, repackaged from the official RPM
