# Repackaged from Signal's official Debian package; the Electron app is
# bundled in /opt/Signal. The .deb's scriptlets are carried over in part: its
# /usr/bin link and polkit policies are installed here, and the update marker
# is touched in %posttrans. chrome-sandbox stays 0755 (Fedora has user
# namespaces), and the AppArmor profile is not needed on Fedora.

%global debug_package %{nil}
%global __strip /bin/true
# Don't export or require the libraries and helper binaries Electron bundles;
# the runtime dependencies are listed by hand, from the .deb's Depends and the
# libraries the binaries link against.
%global __provides_exclude_from ^/opt/Signal/.*$
%global __requires_exclude_from ^/opt/Signal/.*$

Name:           signal-desktop
Version:        8.36.0
Release:        1%{?dist}
Summary:        Private messaging from your desktop

License:        AGPL-3.0-only
URL:            https://signal.org
Source0:        https://updates.signal.org/desktop/apt/pool/s/%{name}/%{name}_%{version}_amd64.deb
ExclusiveArch:  x86_64

BuildRequires:  bsdtar
BuildRequires:  desktop-file-utils

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       cups-libs
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       libnotify
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       nss
# pkcheck asks for your password before showing the recovery key, turning on
# backups or exporting chats; without it Signal skips that check.
Requires:       polkit
# Loaded at run time for audio (the .deb depends on libpulse0).
Requires:       pulseaudio-libs
Requires:       xdg-utils

%description
Signal Desktop links with Signal on your phone for private messaging.


%prep
%setup -q -c -T
bsdtar -xf %{SOURCE0} 'data.tar.*'
bsdtar -xf data.tar.*

%build

%install
cp -a opt usr %{buildroot}/
chmod 0755 %{buildroot}/opt/Signal/chrome-sandbox
# Not used on Fedora; the .deb's postinst only installs it under AppArmor.
rm %{buildroot}/opt/Signal/resources/apparmor-profile
# The .deb's postinst copies the polkit policies here, under these names.
for policy in enable-backups view-aep plaintext-export; do
    install -Dpm 0644 %{buildroot}/opt/Signal/resources/org.signalapp.$policy.policy \
        %{buildroot}%{_datadir}/polkit-1/actions/org.signalapp.signal-desktop.$policy.policy
done
# Upstream points the desktop file at /opt; use the /usr/bin link instead.
sed -i 's|^Exec=/opt/Signal/signal-desktop |Exec=signal-desktop |' \
    %{buildroot}%{_datadir}/applications/%{name}.desktop
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/Signal/signal-desktop %{buildroot}%{_bindir}/signal-desktop
rm -rf %{buildroot}%{_datadir}/doc

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

# A running Signal watches this file and offers to restart into the new
# version when an update touches it, as the .deb's postinst does.
%posttrans
touch /opt/Signal/.signal-postinst || :


%files
/opt/Signal/
%ghost /opt/Signal/.signal-postinst
%{_bindir}/signal-desktop
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/polkit-1/actions/org.signalapp.signal-desktop.*.policy

%changelog
* Thu Nov 19 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.36.0-1
- Update to 8.36.0

* Wed Nov 18 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.35.0-2
- Install the polkit policies and the update marker, as the .deb does
- Keep chrome-sandbox 0755 instead of setuid root; drop the AppArmor profile
- List the runtime dependencies by hand instead of filtering bundled libraries

* Thu Nov 12 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.35.0-1
- Update to 8.35.0

* Thu Nov 05 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.34.0-1
- Update to 8.34.0

* Wed Oct 28 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.33.0-1
- Update to 8.33.0

* Tue Oct 20 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.32.0-1
- Update to 8.32.0

* Fri Oct 16 2026 Maarten van der Rijst <github@feedmebits.nl> - 8.31.0-1
- Initial package, repackaged from the official .deb
