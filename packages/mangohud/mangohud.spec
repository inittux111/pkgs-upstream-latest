%global appname MangoHud
%global forgeurl https://github.com/flightlessmango/MangoHud

# Versions from upstream's subprojects/*.wrap, set by update-hook.
%global imgui_ver 1.91.6
%global vulkan_ver 1.4.346
%global implot_ver 0.16
%global implot_wrap_ver 2

%global tarball_version %%(echo %{version} | tr '~' '-')

# TODO: try to fix amdgpu tests
%bcond_with tests

Name:           mangohud
Version:        0.8.4
%forgemeta
Release:        1%{?dist}
Summary:        Vulkan and OpenGL overlay for monitoring FPS, temperatures, CPU/GPU load

License:        MIT
URL:            %{forgeurl}
Source0:        %{url}/archive/v%{tarball_version}/%{name}-%{tarball_version}.tar.gz
# imgui
Source1:        https://github.com/ocornut/imgui/archive/v%{imgui_ver}/imgui-%{imgui_ver}.tar.gz
# Vulkan-Headers and Vulkan-Utility-Libraries (versions from subprojects/*.wrap)
Source3:        https://github.com/KhronosGroup/Vulkan-Headers/archive/v%{vulkan_ver}/Vulkan-Headers-%{vulkan_ver}.tar.gz
Source4:        https://github.com/KhronosGroup/Vulkan-Utility-Libraries/archive/v%{vulkan_ver}/Vulkan-Utility-Libraries-%{vulkan_ver}.tar.gz
# implot
Source5:        https://github.com/epezent/implot/archive/v%{implot_ver}/implot-%{implot_ver}.tar.gz
Source6:        https://wrapdb.mesonbuild.com/v%{implot_wrap_ver}/implot_%{implot_ver}-1/get_patch#/implot-%{implot_ver}-wrap.zip
Source20:       README.Fedora.md

# MangoHud switched to bundled vulkan-headers since 0.6.9 version. This rebased
# upstream patch which reverts this change.
# https://github.com/flightlessmango/MangoHud/commit/bc282cf300ed5b6831177cf3e6753bc20f48e942
# Patch0:         mangohud-0.6.9-use-system-vulkan-headers.patch

BuildRequires:  vulkan-headers
BuildRequires:  appstream
BuildRequires:  dbus-devel
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  libappstream-glib
BuildRequires:  libstdc++-static
BuildRequires:  meson >= 0.60
BuildRequires:  python3-mako
BuildRequires:  pkgconfig(dri)
BuildRequires:  pkgconfig(glfw3)
BuildRequires:  pkgconfig(glslang)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(spdlog)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xkbcommon)
# Tip and memo if upstream decide to unbundle vulkan-headers
# BuildRequires:  pkgconfig(vulkan) < 1.3.241


%if %{with tests}
BuildRequires:  libcmocka-devel
%endif

Requires:       hicolor-icon-theme
Requires:       vulkan-loader%{?_isa}

Recommends:     (mangohud(x86-32) if glibc(x86-32))

Suggests:       %{name}-mangoplot
Suggests:       goverlay

Provides:       bundled(imgui) = %{imgui_ver}
Provides:       bundled(vulkan-headers) = %{vulkan_ver}
Provides:       bundled(vulkan-utility-libraries) = %{vulkan_ver}
Provides:       bundled(implot) = %{implot_ver}

%global _description %{expand:
A Vulkan and OpenGL overlay for monitoring FPS, temperatures, CPU/GPU load and
more.}

%description %{_description}


%package        mangoplot
Summary:        Local visualization "mangoplot" for %{name}
BuildArch:      noarch

Requires:       %{name} = %{version}-%{release}
Requires:       python3-matplotlib
Requires:       python3-numpy

%description    mangoplot
Local visualization "mangoplot" for %{name}.


%prep
%autosetup -n %{appname}-%{tarball_version} -p1
%setup -qn %{appname}-%{tarball_version} -D -T -a1
%setup -qn %{appname}-%{tarball_version} -D -T -a3
%setup -qn %{appname}-%{tarball_version} -D -T -a4
%setup -qn %{appname}-%{tarball_version} -D -T -a5
%setup -qn %{appname}-%{tarball_version} -D -T -a6

# Meson skips the wraps' patch_directory overlays when the source directory
# already exists, so apply them by hand.
# imgui
mv imgui-%{imgui_ver} subprojects/
cp -a subprojects/packagefiles/imgui-%{imgui_ver}/. subprojects/imgui-%{imgui_ver}/
# Vulkan-Headers
mv Vulkan-Headers-%{vulkan_ver} subprojects/
cp -a subprojects/packagefiles/vulkan-headers/. subprojects/Vulkan-Headers-%{vulkan_ver}/
# Vulkan-Utility-Libraries
mv Vulkan-Utility-Libraries-%{vulkan_ver} subprojects/
cp -a subprojects/packagefiles/vulkan-utility-libraries/. subprojects/Vulkan-Utility-Libraries-%{vulkan_ver}/
# implot
mv implot-%{implot_ver} subprojects/

%if %{with tests}
# Use system cmocka instead of subproject
# https://gitlab.archlinux.org/archlinux/packaging/packages/mangohud/-/blob/0.6.9.1-10/PKGBUILD?ref_type=tags#L32
sed -i "s/  cmocka = subproject('cmocka')//g" meson.build
sed -i "s/cmocka_dep = cmocka.get_variable('cmocka_dep')/cmocka_dep = dependency('cmocka')/g" meson.build
%endif


%build
%meson \
    -Dmangoapp=true \
    -Dmangohudctl=true \
    -Dinclude_doc=true \
    -Duse_system_spdlog=enabled \
    -Dwith_wayland=enabled \
    -Dwith_xnvctrl=disabled \
    %if %{with tests}
    -Dtests=enabled \
    %else
    -Dtests=disabled \
    %endif
    %{nil}
%meson_build


%install
%meson_install

# ERROR: ambiguous python shebang
sed -i "s@#!/usr/bin/env python@#!/usr/bin/python3@" \
    %{buildroot}%{_bindir}/mangoplot

# Install Fedora docs
install -D -p -m 0644 %{SOURCE20} %{buildroot}%{_docdir}/%{name}/README.Fedora.md


%check
# https://github.com/flightlessmango/MangoHud/issues/812
# ? tag-invalid           : stock icon is not valid [io.github.flightlessmango.mangohud]
%dnl appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.xml
%if %{with tests}
%meson_test
%endif


%files
%license LICENSE
%doc README.md
%doc %{_docdir}/%{name}/presets.conf.example
%doc %{_docdir}/%{name}/README.Fedora.md
%{_bindir}/mangoapp
%{_bindir}/mangohud
%{_bindir}/mangohudctl
%{_datadir}/icons/hicolor/scalable/*/*.svg
%{_datadir}/vulkan/implicit_layer.d/*Mango*.json
%{_docdir}/%{name}/%{appname}.conf.example
%{_libdir}/%{name}/
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/mangoapp.1*
%{_metainfodir}/*.metainfo.xml

%files mangoplot
%{_bindir}/mangoplot


%changelog
* Tue Nov 17 2026 Maarten <github@feedmebits.nl> - 0.8.4-1
- Update to 0.8.4

* Tue Nov 17 2026 Maarten <github@feedmebits.nl> - 0.8.3~rc1-1
- Import from Fedora
