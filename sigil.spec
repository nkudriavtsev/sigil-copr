Name:           sigil
Version:        0.7.4
Release:        2%{?dist}
Summary:        WYSIWYG ebook editor

Group:          Applications/Productivity
License:        GPLv3+
URL:            http://code.google.com/p/sigil/
Source0:        http://sigil.googlecode.com/files/Sigil-%{version}-Code.zip
# use system spelling dictionaries
Patch1:         %{name}-0.6.2-system-dicts.patch

BuildRequires:  cmake
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtwebkit-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qtxmlpatterns-devel
BuildRequires:  boost-devel
BuildRequires:  zlib-devel
BuildRequires:  FlightCrew-devel
BuildRequires:  xerces-c-devel >= 3.1
BuildRequires:  hunspell-devel
%if 0%{?fedora} >= 18
BuildRequires:  pcre-devel >= 8.31
%endif
BuildRequires:  minizip-devel
BuildRequires:  desktop-file-utils
Provides:       bundled(libtidy)

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


%prep
%setup -q -c
%patch1 -p1 -b .system-dicts

# remove unbundled stuff
for i in src/*; do
    # lets not remove Sigil itself ...
    if [ "$i" = "src/Sigil" ]; then
        continue
    fi
    # tidyLib is modified to deal with epub, so stick with the bundled copy
    if [ "$i" = "src/tidyLib" ]; then
        continue
    fi
%if 0%{?fedora} < 18
    # pcre >= 8.31 is required for UTF-16 support
    if [ "$i" = "src/pcre" ]; then
        continue
    fi
%endif
    rm -r "$i"
done


%build
mkdir build
cd build
%{cmake} -DBUILD_SHARED_LIBS:BOOL=OFF -DHUNSPELL_DICTS_PATH=%{_datadir}/myspell ..

make %{?_smp_mflags}


%install
cd build
make install DESTDIR=$RPM_BUILD_ROOT
desktop-file-validate $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop


%post
/usr/bin/update-desktop-database &> /dev/null || :

%postun
/usr/bin/update-desktop-database &> /dev/null || :


%files
%doc COPYING.txt ChangeLog.txt
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.png


%changelog
* Mon Nov 11 2013 Rex Dieter <rdieter@fedoraproject.org> 0.7.4-2
- rebuild (qt5 qreal/arm)

* Mon Oct 28 2013 Dan Horák <dan[at]danny.cz> - 0.7.4-1
- New upstream release 0.7.4 (#1023931)

* Wed Sep 11 2013 Dan Horák <dan[at]danny.cz> - 0.7.3-1
- New upstream release 0.7.3 (#907398)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Jul 28 2013 Petr Machata <pmachata@redhat.com> - 0.6.2-3
- Rebuild for boost 1.54.0

* Sat Feb 09 2013 Denis Arnaud <denis.arnaud_fedora@m4x.org> - 0.6.2-2
- Rebuild for Boost-1.53.0

* Tue Dec 18 2012 Dan Horák <dan[at]danny.cz> - 0.6.2-1
- New upstream release 0.6.2

* Sun Nov 25 2012 Hans de Goede <hdegoede@redhat.com> - 0.6.0-3
- Add Provides: bundled(libtidy)  (rhbz#772362)

* Mon Nov 19 2012 Hans de Goede <hdegoede@redhat.com> - 0.6.0-2
- Call desktop-file-validate on the desktop-file (rhbz#772362)

* Wed Oct 31 2012 Dan Horák <dan[at]danny.cz> - 0.6.0-1
- New upstream release 0.6.0

* Sun Oct 21 2012 Dan Horák <dan[at]danny.cz> - 0.5.907-1
- New upstream release 0.5.907 (beta)

* Fri Oct 05 2012 Dan Horák <dan[at]danny.cz> - 0.5.906-2
- allow use of bundled pcre on Fedora < 18
- use system spelling dictionaries

* Thu Oct 04 2012 Dan Horák <dan[at]danny.cz> - 0.5.906-1
- New upstream release 0.5.906 (beta)

* Mon Jan 23 2012 Hans de Goede <hdegoede@redhat.com> - 0.5.0-1
- New upstream release 0.5.0
- Add patches to use system hunspell and pcre libs

* Thu Jan 12 2012 Hans de Goede <hdegoede@redhat.com> - 0.4.2-3
- Drop buildroot and defattr boilerplate (no longer needed with recent rpm)
- Use system FlightCrew and XercesExtensions
- Drop support for building for F-15, having a buildin xerces-c with a shared
  system XercesExtensions is asking for trouble

* Tue Dec 13 2011 Dan Horák <dan[at]danny.cz> - 0.4.2-2
- don't require SSE2 in xerces

* Mon Dec 12 2011 Dan Horák <dan[at]danny.cz> - 0.4.2-1
- initial Fedora version
