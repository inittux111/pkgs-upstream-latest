# Repackaged from Signal's official Debian package; the Electron app is
# bundled in /opt/Signal.

%global debug_package %{nil}
%global __strip /bin/true
# Don't export or require the libraries Electron bundles.
%global __provides_exclude_from ^/opt/Signal/.*$
%global __requires_exclude ^lib(ffmpeg|EGL|GLESv2|vk_swiftshader|vulkan)\\.so.*$

Name:           signal-desktop
Version:        8.33.0
Release:        1%{?dist}
Summary:        Private messaging from your desktop

License:        AGPL-3.0-only
URL:            https://signal.org
Source0:        https://updates.signal.org/desktop/apt/pool/s/%{name}/%{name}_%{version}_amd64.deb
ExclusiveArch:  x86_64

BuildRequires:  bsdtar
BuildRequires:  desktop-file-utils

%description
Signal Desktop links with Signal on your phone for private messaging.


%prep
%setup -q -c -T
bsdtar -xf %{SOURCE0} 'data.tar.*'
bsdtar -xf data.tar.*

%build

%install
cp -a opt usr %{buildroot}/
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/Signal/signal-desktop %{buildroot}%{_bindir}/signal-desktop
rm -rf %{buildroot}%{_datadir}/doc

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop


%files
/opt/Signal/
%attr(4755,root,root) /opt/Signal/chrome-sandbox
%{_bindir}/signal-desktop
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
* Wed Oct 28 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.33.0-1
- Update to 8.33.0

* Tue Oct 20 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.32.0-1
- Update to 8.32.0

* Fri Oct 16 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.31.0-1
- Initial package, repackaged from the official .deb
