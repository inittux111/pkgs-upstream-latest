# Repackaged from pear-desktop's official RPM; the Electron app is bundled in
# "/opt/YouTube Music". The upstream RPM's scriptlets are not carried over:
# its /usr/bin link is created here, chrome-sandbox stays 0755 (Fedora has
# user namespaces), and the rest (AppArmor, cache refreshes) is not needed on
# Fedora.

%global debug_package %{nil}
%global __strip /bin/true
# Don't export or require the libraries and helper binaries Electron bundles;
# the runtime dependencies are listed by hand (upstream's RPM only lists
# libuuid), from the libraries the binaries link against.
%global __provides_exclude_from ^/opt/YouTube Music/.*$
%global __requires_exclude_from ^/opt/YouTube Music/.*$

Name:           youtube-music
Version:        3.12.1
Release:        2%{?dist}
Summary:        YouTube Music desktop app with custom plugins

License:        MIT
URL:            https://github.com/pear-devs/pear-desktop
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.x86_64.rpm
ExclusiveArch:  x86_64

BuildRequires:  cpio
BuildRequires:  desktop-file-utils

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       cups-libs
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
Pear (formerly YouTube Music Desktop App) wraps YouTube Music in a desktop
app and adds plugins such as ad blocking, a downloader and Discord status.


%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idm --quiet

%build

%install
cp -a opt usr %{buildroot}/
chmod 0755 "%{buildroot}/opt/YouTube Music/chrome-sandbox"
# Not used on Fedora; the upstream scriptlet only installs it under AppArmor.
rm "%{buildroot}/opt/YouTube Music/resources/apparmor-profile"
# Upstream points the desktop file at /opt; use the /usr/bin link instead.
sed -i 's|^Exec="/opt/YouTube Music/youtube-music" |Exec=youtube-music |' \
    %{buildroot}%{_datadir}/applications/com.github.th-ch.youtube-music.desktop
mkdir -p %{buildroot}%{_bindir}
ln -s "/opt/YouTube Music/youtube-music" %{buildroot}%{_bindir}/youtube-music

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.github.th-ch.youtube-music.desktop


%files
"/opt/YouTube Music/"
%{_bindir}/youtube-music
%{_datadir}/applications/com.github.th-ch.youtube-music.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
* Wed Nov 18 2026 Maarten van der Rijst <github@feedmebits.nl> - 3.12.1-2
- List the runtime dependencies by hand instead of filtering bundled libraries
- Drop the AppArmor profile; start the /usr/bin link from the desktop file

* Sun Nov 15 2026 Maarten van der Rijst <github@feedmebits.nl> - 3.12.1-1
- Update to 3.12.1

* Fri Oct 16 2026 Maarten van der Rijst <github@feedmebits.nl> - 3.12.0-1
- Initial package, repackaged from the official RPM
