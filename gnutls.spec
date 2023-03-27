Name: gnutls
Version: 3.6.14
Release: 12
Summary: The GNU Secure Communication Protocol Library

License: LGPLv2.1+ and GPLv3+
URL: https://www.gnutls.org/
Source0: https://www.gnupg.org/ftp/gcrypt/%{name}/v3.6/%{name}-%{version}.tar.xz
Source1: https://www.gnupg.org/ftp/gcrypt/%{name}/v3.6/%{name}-%{version}.tar.xz.sig

Patch1: fix-ipv6-handshake-failed.patch
Patch2: handshake-reject-no_renegotiation-alert-if-handshake.patch
Patch3: backport-tests-check_for_datefudge-don-t-exit-the-test-progra.patch
Patch4: backport-tests-remove-launch_pkcs11_server.patch
Patch5: backport-testpkcs11-use-datefudge-to-trick-certificate-expiry.patch
Patch6: backport-CVE-2021-20231.patch
Patch7: backport-CVE-2021-20232.patch
Patch8: backport-CVE-2022-2509.patch
Patch9: backport-CVE-2021-4209.patch
Patch10: backport-01-CVE-2023-0361.patch
Patch11: backport-02-CVE-2023-0361.patch
Patch12: backport-x86-add-detection-of-instruction-set-on-Zhaoxin-CPU.patch

%bcond_without dane
%bcond_with guile
%bcond_without fips

BuildRequires: p11-kit-devel, gettext-devel, zlib-devel, readline-devel
BuildRequires: libtasn1-devel, libtool, automake, autoconf, texinfo
BuildRequires: autogen-libopts-devel, autogen, gperf, gnupg2, gcc, gcc-c++
BuildRequires: nettle-devel, trousers-devel, libidn2-devel
BuildRequires: libunistring-devel, net-tools, softhsm
BuildRequires: p11-kit-trust, ca-certificates
%if %{with fips}
BuildRequires: fipscheck
%endif
%if %{with dane}
BuildRequires: unbound-devel unbound-libs
%endif
%if %{with guile}
BuildRequires: guile22-devel
%endif

Requires: crypto-policies, p11-kit-trust, libtasn1, nettle
Recommends: trousers >= 0.3.11.2

Provides: bundled(gnulib) = 20130424
Provides: gnutls-c++ = %{version}-%{release}
Provides: gnutls-dane = %{version}-%{release}
Obsoletes: gnutls-c++ < %{version}-%{release} 
Obsoletes: gnutls-dane < %{version}-%{release}

%description
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS
protocols and technologies around them. It provides a simple C language
application programming interface (API) to access the secure communications
protocols as well as APIs to parse and write X.509, PKCS #12, and other
required structures.
The project strives to provide a secure communications back-end, simple to use
and integrated with the rest of the base Linux libraries. A back-end designed
to work and be secure out of the box, keeping the complexity of TLS and PKI out
of application code.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: pkgconf

%description devel
This package contains files needed for developing applications with %{name}.

%package utils
License: GPLv3+
Summary: Command line tools for TLS protocol
Requires: %{name}%{?_isa} = %{version}-%{release}

%description utils
GnuTLS is a secure communications library implementing the SSL,TLS and DTLS protocols
and technologies around them. It provides a simple c language application programming
interface(API) to access the secure communication protocols as well as APIs to parse
and write X.509, PKCS #12, OpenPGP and other required structures.
This package contains command line TLS client and server certificate manipulation tools.

%package_help

%if %{with guile}
%package guile
Summary: Guile bindings for the GNUTLS library
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: guile

%description guile
This package contains Guile bindings for the library.
%endif


%prep
%autosetup -n %{name}-%{version} -p1
autoreconf

sed -i -e 's|sys_lib_dlsearch_path_spec="/lib /usr/lib|sys_lib_dlsearch_path_spec="/lib /usr/lib %{_libdir}|g' configure
rm -f lib/minitasn1/*.c lib/minitasn1/*.h
rm -f src/libopts/*.c src/libopts/*.h src/libopts/compat/*.c src/libopts/compat/*.h

echo "SYSTEM=NORMAL" >> tests/system.prio

# Note that we explicitly enable SHA1, as SHA1 deprecation is handled
# via the crypto policies

%build
CCASFLAGS="$CCASFLAGS -Wa,--generate-missing-build-notes=yes"
export CCASFLAGS

# These should be checked by m4/guile.m4 instead of configure.ac
# taking into account of _guile_suffix
guile_snarf=%{_bindir}/guile-snarf2.2
export guile_snarf
GUILD=%{_bindir}/guild2.2
export GUILD

%configure --with-libtasn1-prefix=%{_prefix} \
%if %{with fips}
           --enable-fips140-mode \
%endif
	       --enable-sha1-support \
           --disable-static \
           --disable-openssl-compatibility \
           --disable-non-suiteb-curves \
           --with-system-priority-file=%{_sysconfdir}/crypto-policies/back-ends/gnutls.config \
           --with-default-trust-store-pkcs11="pkcs11:" \
           --with-trousers-lib=%{_libdir}/libtspi.so.1 \
           --htmldir=%{_docdir}/manual \
%if %{with guile}
           --enable-guile \
           --with-guile-extension-dir=%{_libdir}/guile/2.2 \
%else
           --disable-guile \
%endif
%if %{with dane}
           --with-unbound-root-key-file=/var/lib/unbound/root.key \
           --enable-dane \
%else
           --disable-dane \
%endif
           --disable-rpath \
           --with-default-priority-string="@SYSTEM"


 
make %{?_smp_mflags} V=1
 
%if %{with fips}
%define __spec_install_post \
	%{?__debug_package:%{__debug_install_post}} \
	%{__arch_install_post} \
	%{__os_install_post} \
	fipshmac -d $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_libdir}/libgnutls.so.30.*.* \
	file=`basename $RPM_BUILD_ROOT%{_libdir}/libgnutls.so.30.*.hmac` && mv $RPM_BUILD_ROOT%{_libdir}/$file $RPM_BUILD_ROOT%{_libdir}/.$file && ln -s .$file $RPM_BUILD_ROOT%{_libdir}/.libgnutls.so.30.hmac \
%{nil}
%endif

%install
make install DESTDIR=$RPM_BUILD_ROOT
make -C doc install-html DESTDIR=$RPM_BUILD_ROOT

%delete_la_and_a
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_libdir}/gnutls/libpkcs11mock1.*
%if %{without dane}
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/gnutls-dane.pc
%endif
 
%find_lang gnutls

%check
make check %{?_smp_mflags}

%files -f gnutls.lang
%defattr(-,root,root)
%doc README.md AUTHORS
%license LICENSE doc/COPYING doc/COPYING.LESSER
%if %{with dane}
%{_libdir}/libgnutls-dane.so.*
%endif
%{_libdir}/libgnutls.so.30*
%{_libdir}/libgnutlsxx.so.*
%if %{with fips}
%{_libdir}/.libgnutls.so.*.hmac
%endif

%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/*.pc
%{_libdir}/libgnutls*.so
%{_includedir}/*

%files utils
%{_bindir}/certtool
%{_bindir}/tpmtool
%{_bindir}/ocsptool
%{_bindir}/psktool
%{_bindir}/p11tool
%{_bindir}/srptool
%{_bindir}/gnutls*
%if %{with dane}
%{_bindir}/danetool
%endif

%files help
%defattr(-,root,root)
%doc NEWS THANKS doc/certtool.cfg
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_infodir}/gnutls*
%{_infodir}/pkcs11-vision*
%{_docdir}/manual/*

%if %{with guile}
%files guile
%defattr(-,root,root)
%{_libdir}/guile/2.2/guile-gnutls*.so*
%{_libdir}/guile/2.2/site-ccache/gnutls.go
%{_libdir}/guile/2.2/site-ccache/gnutls/extra.go
%{_datadir}/guile/site/2.2/gnutls.scm
%{_datadir}/guile/site/2.2/gnutls/extra.scm
%endif

%changelog
* MON Feb 27 2023 xuraoqing <xuraoqing@huawei.com> - 3.6.14-12
- x86 add detection of instruction set on Zhaoxin CPU

* Thu Feb 16 2023 xuraoqing <xuraoqing@huawei.com> - 3.6.14-11
- fix CVE-2023-0361 

* Thu Sep 1 2022 xuraoqing <xuraoqing@huawei.com> - 3.6.14-10
- Detach the sub package gnutls-utils from gnutls

* Mon Aug 29 2022 yanglongkang <yanglongkang@h-partners.com> - 3.6.14-9
- fix CVE-2021-4209

* Fri Aug 5 2022 dongyuzhen <dongyuzhen@h-partners.com> - 3.6.14-8
- fix CVE-2022-2509

* Mon Mar 22 2021 yixiangzhike <zhangxingliang3@huawei.com> - 3.6.14-7
- fix CVE-2021-20231 CVE-2021-20232

* Sat Jan 30 2021 lirui <lirui130@huawei.com> - 3.6.14-6
- backport upsteam patches to fix testpkcs11.sh test failed

* Fri Dec 18 2020 liquor <lirui130@huawei.com> - 3.6.14-5
- add skip_if_no_datefudge function

* Wed Dec 16 2020 liquor <lirui130@huawei.com> - 3.6.14-4
- revert "Detach the sub package gnutls-utils from gnutls"

* Fri Oct 16 2020 zhangxingliang <zhangxingliang3@huawei.com> - 3.6.14-3
- Detach the sub package gnutls-utils from gnutls

* Fri Sep 4 2020 yangzhuangzhuang <yangzhuangzhuang1@huawei.com> - 3.6.14-2
- reject no_renegotiation alert if handshake is incomplete

* Thu Aug 6 2020 wangchen <wangchen137@huawei.com> - 3.6.14-1
- update to 3.6.14

* Mon Jun 8 2020 Anakin Zhang <benjamin93@163.com> - 3.6.9-7
- fix x509 drop endless loop and pkcs12 iterations

* Wed Apr 22 2020 Anakin Zhang <benjamin93@163.com> - 3.6.9-6
- fix CVE-2020-11501

* Fri Jan 10 2020 openEuler Buildteam <buildteam@openeuler.org> - 3.6.9-5
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:clean code

* Tue Nov 5 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.6.9-4
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:delete redundant .hmac files in devel package

* Thu Oct 24 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.6.9-3
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:remove the datefudge from buildRequires

* Tue Sep 24 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.6.9-2
- Require adjust

* Wed Sep 11 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.6.9-1
- Package init
