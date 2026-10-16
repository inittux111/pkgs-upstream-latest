# Repackaged from pear-desktop's official RPM; the Electron app is bundled in
# "/opt/YouTube Music". The upstream RPM's scriptlets are not carried over:
# its /usr/bin link is created here, and the rest (AppArmor, cache refreshes)
# is not needed on Fedora.

%global debug_package %{nil}
%global __strip /bin/true
# Don't export or require the libraries Electron bundles.
%global __provides_exclude_from ^/opt/YouTube Music/.*$
%global __requires_exclude ^lib(ffmpeg|EGL|GLESv2|vk_swiftshader|vulkan)\\.so.*$

Name:           youtube-music
Version:        3.12.0
Release:        1%{?dist}
Summary:        YouTube Music desktop app with custom plugins

License:        MIT
URL:            https://github.com/pear-devs/pear-desktop
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.x86_64.rpm
ExclusiveArch:  x86_64

BuildRequires:  cpio
BuildRequires:  desktop-file-utils

Requires:       libuuid

%description
Pear (formerly YouTube Music Desktop App) wraps YouTube Music in a desktop
app and adds plugins such as ad blocking, a downloader and Discord status.


%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idm --quiet

%build

%install
cp -a opt usr %{buildroot}/
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
* Fri Oct 16 2026 Maarten van der Rijst <github@feedmebits.nl> - 3.12.0-1
- Initial package, repackaged from the official RPM
