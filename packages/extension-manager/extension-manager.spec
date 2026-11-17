# Built from source: upstream only publishes a Flatpak, no RPM or DEB.

%global app_id com.mattjakeman.ExtensionManager

Name:           extension-manager
Version:        0.7.0
Release:        1%{?dist}
Summary:        A utility for browsing and installing GNOME Shell Extensions

License:        GPL-3.0-or-later
URL:            https://github.com/mjakeman/extension-manager
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  blueprint-compiler
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.8
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(glycin-2)
BuildRequires:  pkgconfig(glycin-gtk4-2)

Requires:       hicolor-icon-theme

%description
A native tool for browsing, installing, and managing GNOME Shell Extensions.


%prep
%autosetup -p1

%build
# Fedora doesn't package libbacktrace, which only adds stack traces to the
# crash dialog.
%meson -Dbacktrace=false -Dpackage=RPM -Ddistributor=pkgs-upstream-latest
%meson_build

%install
%meson_install
%find_lang %{name}

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{app_id}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{app_id}.metainfo.xml


%files -f %{name}.lang
%license COPYING
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/dbus-1/services/%{app_id}.service
%{_datadir}/glib-2.0/schemas/%{app_id}.gschema.xml
%{_datadir}/gnome-shell/search-providers/%{app_id}.search-provider.ini
%{_datadir}/icons/hicolor/scalable/apps/%{app_id}.svg
%{_datadir}/icons/hicolor/symbolic/apps/%{app_id}-symbolic.svg
%{_metainfodir}/%{app_id}.metainfo.xml

%changelog
* Tue Nov 17 2026 Maarten <github@feedmebits.nl> - 0.7.0-1
- Initial package
