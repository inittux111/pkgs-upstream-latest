# Built with cargo straight from crates.io, so the COPR project needs network
# access during builds (copr.conf: COPR_ENABLE_NET). --locked keeps the
# dependency versions pinned to upstream's Cargo.lock.

Name:           starship
Version:        1.26.0
Release:        1%{?dist}
Summary:        Minimal, blazing-fast and infinitely customizable prompt for any shell

License:        ISC
URL:            https://github.com/starship/starship
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc

%description
Starship is a minimal, blazing-fast and infinitely customizable prompt for
any shell (bash, zsh, fish and more). It shows the information you need
while you work, like the git status or the language versions of a project.


%prep
%autosetup -p1

%build
export RUSTFLAGS="%{build_rustflags}"
cargo build --release --locked

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

mkdir -p %{buildroot}%{bash_completions_dir} %{buildroot}%{zsh_completions_dir} \
         %{buildroot}%{fish_completions_dir}
target/release/%{name} completions bash >%{buildroot}%{bash_completions_dir}/%{name}
target/release/%{name} completions zsh  >%{buildroot}%{zsh_completions_dir}/_%{name}
target/release/%{name} completions fish >%{buildroot}%{fish_completions_dir}/%{name}.fish

%check
%{buildroot}%{_bindir}/%{name} --version


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}
%{zsh_completions_dir}/_%{name}
%{fish_completions_dir}/%{name}.fish

%changelog
* Fri Oct 16 2026 Maarten van der Rijst <github@feedmebits.nl> - 1.26.0-1
- Initial package
