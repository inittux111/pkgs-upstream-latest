# Based on Fedora's btrfs-assistant.spec, updated for the 3.x layout
# (privileged helper daemon over D-Bus + systemd unit).

Name:           btrfs-assistant
Version:        3.0.0
Release:        1%{?dist}
Summary:        GUI management tool to make managing a Btrfs filesystem easier

License:        GPL-3.0-or-later
URL:            https://gitlab.com/%{name}/%{name}
Source0:        https://gitlab.com/%{name}/%{name}/-/archive/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  btrfs-progs-devel
BuildRequires:  libbtrfsutil
BuildRequires:  pkgconfig(Qt6Widgets)
BuildRequires:  pkgconfig(Qt6DBus)
BuildRequires:  cmake(Qt6LinguistTools)
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  systemd-rpm-macros

Requires:       btrfs-progs
Requires:       dbus
Requires:       hicolor-icon-theme
Requires:       polkit

Recommends:     btrfsmaintenance
Recommends:     snapper

%description
Btrfs Assistant is a GUI management tool to make managing a Btrfs filesystem
easier. It offers an overview of Btrfs metadata, subvolume and snapshot
management, scrub and balance operations, and front-ends for Snapper and
Btrfs Maintenance.


%prep
%autosetup -p1

# Fix config path for btrfsmaintenance
sed -i 's|^bm_config =.*|bm_config = %{_sysconfdir}/sysconfig/btrfsmaintenance|' src/btrfs-assistant.conf

%build
%cmake -DBTRFS_ASSISTANT_HELPER_LIBEXEC=ON -DBTRFS_ASSISTANT_SYSTEMD_UNIT_DIR=%{_unitdir}
%cmake_build

%install
%cmake_install

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{name}.metainfo.xml

%post
%systemd_post btrfs-assistant-helper.service

%preun
%systemd_preun btrfs-assistant-helper.service

%postun
%systemd_postun_with_restart btrfs-assistant-helper.service


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}-helper
%{_unitdir}/%{name}-helper.service
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_metainfodir}/%{name}.metainfo.xml
%{_datadir}/dbus-1/system-services/org.btrfsassistant.Helper1.service
%{_datadir}/dbus-1/system.d/org.btrfsassistant.Helper1.conf
%{_datadir}/polkit-1/actions/org.btrfsassistant.policy
%config(noreplace) %{_sysconfdir}/%{name}.conf

%changelog
* Fri Oct 16 2026 Maarten van der Rijst <github@feedmebits.nl> - 3.0.0-1
- Update to 3.0.0 (privileged helper daemon over D-Bus + systemd unit)
