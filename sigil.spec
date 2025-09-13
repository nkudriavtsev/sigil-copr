%global __cmake_in_source_build 1

Name:           sigil
Version:        2.6.2
Release:        1%{?dist}
Summary:        WYSIWYG ebook editor
License:        GPLv3+
URL:            https://sigil-ebook.com/
Source0:        https://github.com/Sigil-Ebook/Sigil/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}.appdata.xml
Patch1:         %{name}-0.8.0-system-dicts.patch
Patch2:         %{name}-0.9.3-global-plugin-support.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1632199
# port to minizip 2.x for F-30+
Patch3:         %{name}-1.9.2-minizip2.patch
BuildRequires:  cmake
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtwebengine-devel
BuildRequires:  zlib-devel
BuildRequires:  hunspell-devel
BuildRequires:  pcre-devel >= 8.31
BuildRequires:  pcre2-devel
BuildRequires:  minizip-devel
BuildRequires:  pkgconfig
BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils libappstream-glib
# For the plugins
Requires:       python3
Requires:       python3-pillow python3-cssselect python3-cssutils
Requires:       python3-html5lib python3-lxml python3-qt5
Requires:       python3-regex python3-chardet python3-six
Requires:       hicolor-icon-theme
Recommends:     FlightCrew-sigil-plugin
# See internal/about.md for rationale for this
Provides:       bundled(gumbo)

%description
Sigil is a multi-platform WYSIWYG ebook editor. It is designed to edit books
in ePub format.

Now what does it have to offer...

    * Full Unicode support: everything you see in Sigil is in UTF-16
    * Full EPUB spec support
    * WYSIWYG editing
    * Multiple Views: Book View, Code View and Split View
    * Metadata editor with full support for all possible metadata entries with
      full descriptions for each
    * Table Of Contents editor
    * Multi-level TOC support
    * Book View fully supports the display of any XHTML document possible under
      the OPS spec
    * SVG support
    * Basic XPGT support
    * Advanced automatic conversion of all imported documents to Unicode
    * Currently imports TXT, HTML and EPUB files; more will be added with time
    * Embedded HTML Tidy; all imported documents are thoroughly cleaned;
      changing views cleans the document so no matter how much you screw up
      your code, it will fix it (usually) 


%package doc
License:        CC-BY-SA
Summary:        Documentation for Sigil ebook editor
BuildArch:      noarch

%description doc
%{summary}.


%prep
%setup -q -n Sigil-%{version}
%patch -P 1 -p1
%patch -P 2 -p1
%if 0%{?fedora} >= 30
%patch -P 3 -p1 -b .mz
%endif
sed -i 's|/lib/sigil|/%{_lib}/sigil|'      \
  CMakeLists.txt src/CMakeLists.txt        \
  src/Resource_Files/bash/sigil-sh_install
# Cleanup sources a bit
fixtimestamp() {
  touch -r $1.orig $1
  rm -f $1.orig
}
chmod a-x src/Dialogs/AddSemantics.{cpp,h} \
          src/Form_Files/{AddSemantics,PKeyboardShortcutsWidget}.ui \
          src/Resource_Files/dictionaries/*.{aff,dic} \
          src/Resource_Files/main/*.svg \
          src/Resource_Files/polyfills/MathJax_README.md \
          src/ResourceObjects/NavProcessor.{cpp,h}
for fil in src/Resource_Files/python3lib/metadata_utils.py \
           src/Resource_Files/python3lib/metaproc2.py \
           src/Resource_Files/python3lib/metaproc3.py \
           src/Resource_Files/python3lib/opf_newparser.py
do
  sed -i.orig 's/\r//' $fil
  fixtimestamp $fil
done
for fil in $(grep -Frl %{_bindir}/env .); do
  sed -ri.orig 's,%{_bindir}/env python3?,%{_bindir}/python3,' $fil
  fixtimestamp $fil
done

# Fix hunspell library lookup from python
hver=$(ls -1 %{_libdir}/libhunspell*.so | sed 's/.*hunspell\(-.*\)\.so/\1/')
sed -i.orig "s/find_library('hunspell')/find_library('hunspell$hver')/" \
  src/Resource_Files/plugin_launchers/python/pluginhunspell.py
fixtimestamp src/Resource_Files/plugin_launchers/python/pluginhunspell.py


%build
mkdir build
pushd build
%{cmake} --no-warn-unused-cli -DUSE_SYSTEM_LIBS=1 -DSYSTEM_LIBS_REQUIRED=1 \
  -DINSTALL_BUNDLED_DICTS=0 -DSHARE_INSTALL_PREFIX:PATH=%{_prefix} ..
make %{?_smp_mflags}
popd


%install
pushd build
%make_install
popd
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/plugins
# Make rpmlint happy
chmod +x $RPM_BUILD_ROOT%{_datadir}/%{name}/python3lib/*.py
chmod +x $RPM_BUILD_ROOT%{_datadir}/%{name}/plugin_launchers/python/*.py
chmod -x $RPM_BUILD_ROOT%{_datadir}/%{name}/plugin_launchers/python/sigil_gumbo_bs4_adapter.py
# desktop-file, icons and appdata
desktop-file-validate $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop
rm $RPM_BUILD_ROOT%{_datadir}/pixmaps/%{name}.png
for i in 16 32 48 128 256 512; do
  mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps
  install -p -m 644 src/Resource_Files/icon/app_icons_orig/app_icon_$i.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done
mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps
install -p -m 644 src/Resource_Files/icon/app_icons_orig/app_icon_scalable.svg \
  $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

mkdir -p $RPM_BUILD_ROOT%{_datadir}/appdata
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/appdata
appstream-util validate-relax --nonet \
  $RPM_BUILD_ROOT%{_datadir}/appdata/%{name}.appdata.xml


%files
%doc ChangeLog.txt README.md
%license COPYING.txt
%{_bindir}/%{name}
%{_libdir}/%{name}
%{_datadir}/%{name}
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%files doc
%doc docs/*.epub


%changelog
%autochangelog
