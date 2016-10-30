#
# Conditional build:
%bcond_without	tests
# Don't turn on systems if test suite fails.
# Test suite works fine with bundled libs, so the only way
# to turn on system libs is to make sure test suite works
# with them, too.
%bcond_without	system_admesh
%bcond_without	system_poly2tri
%bcond_with	system_polyclipping
#
%define		admesh_ver		0.98.1
%define		perl_encode_locale_ver	1.05
%define		perl_threads_ver	2.00
#
%include	/usr/lib/rpm/macros.perl
Summary:	G-code generator for 3D printers (RepRap, Makerbot, Ultimaker etc.)
Summary(pl.UTF-8):	Generator G-code dla drukarek 3D (RepRap, Makerbot, Ultimaker itp.)
Name:		slic3r
Version:	1.2.9
Release:	3
License:	AGPL v3 (code), CC-BY (images)
Group:		Applications/Engineering
Source0:	https://github.com/alexrj/Slic3r/archive/%{version}.tar.gz
# Source0-md5:	05ac7b137cbb7b12f442776e4c12dcc2
Source1:	%{name}.desktop
Source2:	%{name}.appdata.xml
# Modify Build.PL so we are able to build this on Fedora
Patch0:		%{name}-buildpl.patch
# Don't warn for Perl >= 5.16
# Use /usr/share/slic3r as datadir
# Those two are located at the same place at the code, so the patch is merged
Patch1:		%{name}-nowarn-datadir.patch
Patch2:		%{name}-english-locale.patch
Patch3:		%{name}-linker.patch
Patch4:		%{name}-clipper.patch
URL:		http://slic3r.org/
BuildRequires:	ImageMagick
BuildRequires:	boost-devel
BuildRequires:	desktop-file-utils
BuildRequires:	perl(ExtUtils::MakeMaker) >= 6.80
BuildRequires:	perl(ExtUtils::ParseXS) >= 3.22
BuildRequires:	perl(ExtUtils::Typemaps::Default) >= 1.05
BuildRequires:	perl(Growl::GNTP) >= 0.15
BuildRequires:	perl(Math::ConvexHull) >= 1.0.4
BuildRequires:	perl(Math::Geometry::Voronoi) >= 1.3
BuildRequires:	perl(Math::PlanePath) >= 53
BuildRequires:	perl(Module::Build::WithXSpp) >= 0.14
BuildRequires:	perl(Moo) >= 1.003001
BuildRequires:	perl-Class-XSAccessor
BuildRequires:	perl-Encode-Locale >= %{perl_encode_locale_ver}
BuildRequires:	perl-ExtUtils-Typemap
BuildRequires:	perl-IO-stringy
BuildRequires:	perl-Math-ConvexHull-MonotoneChain
BuildRequires:	perl-SVG
BuildRequires:	perl-Wx
BuildRequires:	perl-XML-SAX
BuildRequires:	perl-XML-SAX-ExpatXS
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	perl-modules
BuildRequires:	perl-threads >= %{perl_threads_ver}
%{?with_system_poly2tri:BuildRequires:	poly2tri-devel}
%{?with_system_polyclipping:BuildRequires:	polyclipping-devel >= 6.2.9}
BuildRequires:	rpm-perlprov >= 4.1-13
%if %{with system_admesh}
BuildRequires:	admesh-devel >= %{admesh_ver}
Requires:	admesh-libs >= %{admesh_ver}
%endif
Requires:	perl-Encode-Locale >= %{perl_encode_locale_ver}
Requires:	perl-threads >= %{perl_threads_ver}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Slic3r is a G-code generator for 3D printers. It's compatible with
RepRaps, Makerbots, Ultimakers and many more machines. See the project
homepage at http://slic3r.org/ and the documentation on the Slic3r
wiki for more information.

%description -l pl.UTF-8
Slic3r to generator G-code dla drukarek 3D. Jest zgodny z urządzeniami
RepRap, Makerbot, Ultimaker i wieloma innymi. Więcej informacji można
znaleźć na stronie projektu http://slic3r.org/ oraz na wiki projektu
Slic3r.

%prep
%setup -qn Slic3r-%{version}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%{?with_system_polyclipping:%patch4 -p1}

# Remove bundled admesh, clipper, poly2tri and boost
%{?with_system_admesh:%{__rm} -r xs/src/admesh}
%{?with_system_polyclipping:%{__rm} xs/src/clipper.*pp}
%{?with_system_poly2tri:%{__rm} -r xs/src/poly2tri}
%{__rm} -r xs/src/boost

%build
cd xs
%{?with_system_admesh:SYSTEM_ADMESH=1} \
%{?with_system_polyclipping:SYSTEM_POLYCLIPPING=1} \
%{?with_system_poly2tri:SYSTEM_POLY2TRI=1} \
%{__perl} ./Build.PL \
	installdirs=vendor \
	optimize="%{rpmcflags}"
./Build
cd ..

%if %{with tests}
cd xs
./Build test verbose=1
cd -
SLIC3R_NO_AUTO=1 \
%{__perl} Build.PL \
	installdirs=vendor
# the --gui runs no tests, it only checks requires
%endif

# prepare pngs in mutliple sizes
for res in 16 32 48 128 256; do
  mkdir -p hicolor/${res}x${res}/apps
done
cd hicolor
convert ../var/Slic3r.ico %{name}.png
cp %{name}-0.png 256x256/apps/%{name}.png
cp %{name}-1.png 128x128/apps/%{name}.png
cp %{name}-2.png 48x48/apps/%{name}.png
cp %{name}-3.png 32x32/apps/%{name}.png
cp %{name}-4.png 16x16/apps/%{name}.png
rm %{name}-*.png
cd -

# To avoid "iCCP: Not recognized known sRGB profile that has been edited"
cd var
find . -type f -name "*.png" -exec convert {} -strip {} \;
cd -

%install
rm -rf $RPM_BUILD_ROOT
cd xs
./Build install destdir=$RPM_BUILD_ROOT create_packlist=0
cd -
find $RPM_BUILD_ROOT -type f -name '*.bs' -size 0 -exec rm -f {} \;

# I see no way of installing slic3r with it's build script
# So I copy the files around manually
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{perl_vendorlib}
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}
install -d $RPM_BUILD_ROOT%{_datadir}/icons
install -d $RPM_BUILD_ROOT%{_datadir}/appdata

cp -a %{name}.pl $RPM_BUILD_ROOT%{_bindir}/%{name}
cp -a lib/* $RPM_BUILD_ROOT%{perl_vendorlib}

cp -a var/* $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -r hicolor $RPM_BUILD_ROOT%{_datadir}/icons
desktop-file-install --dir=$RPM_BUILD_ROOT%{_desktopdir} %{SOURCE1}

cp %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/appdata/%{name}.appdata.xml

%{_fixperms} $RPM_BUILD_ROOT*

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_icon_cache hicolor

%postun
if [ $1 -eq 0 ] ; then
	%update_icon_cache hicolor
fi

%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_bindir}/%{name}
%{perl_vendorlib}/Slic3r*
%{perl_vendorarch}/Slic3r*
%{perl_vendorarch}/auto/Slic3r*
%{_iconsdir}/hicolor/*/apps/%{name}.png
%{_desktopdir}/%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/%{name}
