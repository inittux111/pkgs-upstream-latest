# Spec written by `pkg add`: cargo downloads the crates at build time
# (COPR_ENABLE_NET=on in copr.conf).

Name:           whatsup-desktop
Version:        1.0.0
Release:        1%{?dist}
Summary:        TODO: one-line summary

License:        TODO
URL:            https://github.com/inittux111/whatsup-desktop
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc

%description
TODO: description


%prep
%autosetup -p1

%build
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
mkdir -p %{buildroot}%{_bindir}
find target/release -maxdepth 1 -type f -perm -u+x ! -name "*.so" \
    -exec install -pm 0755 -t %{buildroot}%{_bindir} {} +


%files
%doc README.md
%{_bindir}/*

%changelog
* Sat Oct 17 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.0.0-1
- Initial package
