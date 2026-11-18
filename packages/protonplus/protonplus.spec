# Built from source: upstream publishes no RPM or DEB, only AppImages.

%global app_id com.vysp3r.ProtonPlus

Name:           protonplus
Version:        0.6.8
Release:        1%{?dist}
Summary:        A modern compatibility tools manager

License:        GPL-3.0-or-later
URL:            https://github.com/Vysp3r/ProtonPlus
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  vala
BuildRequires:  gettext
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig(appstream)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(gee-0.8)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.6
BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(sdl3) >= 3.2.0

Requires:       hicolor-icon-theme

%description
ProtonPlus is a compatibility tools manager: it installs and updates Proton,
Wine and DXVK variants for Steam, Lutris, Heroic and Bottles.


%prep
%autosetup -p1 -n ProtonPlus-%{version}

%build
%meson
%meson_build

%install
%meson_install
%find_lang %{app_id}

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{app_id}.desktop


%files -f %{app_id}.lang
%license LICENSE.md
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/glib-2.0/schemas/%{app_id}.gschema.xml
%{_datadir}/icons/hicolor/*/apps/%{app_id}.png
%{_metainfodir}/%{app_id}.metainfo.xml

%changelog
* Tue Nov 17 2026 Maarten <github@feedmebits.nl> - 0.6.8-1
- Initial package
