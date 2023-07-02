%define module_name apple-bce
%define kname	apple-bce

Summary: Apple BCE (Buffer Copy Engine) and associated subsystems drivers for Intel T2-based Macs
Name: dkms-%{module_name}
Version: 0.1
Release: 1
ExclusiveArch: %{x86_64}
Url:      https://github.com/t2linux/apple-bce-drv
Source0:  https://github.com/t2linux/apple-bce-drv/archive/7f90a5f6048b1315299a6a7ac286eef1088c764e.zip
Group:		Hardware
License:	distributable
BuildRequires: clang, dkms, kmod, kernel-rc-desktop-devel

%description
MacBook Bridge/T2 Linux Driver

A driver for MacBook models 2018 and newer,
implementing the VHCI (required for mouse/keyboard/etc.) and audio functionality.

The project is divided into 3 main components:

BCE (Buffer Copy Engine) - this is what the files in the root directory are for.
This estabilishes a basic communication channel with the T2.
VHCI and Audio both require this component.

VHCI - this is a virtual USB host controller; keyboard, mouse and other system
components are provided by this component.
Currently the trackpad does not work on macbooks, only the built-in keyboard.

Audio - a driver for the T2 audio interface,
currently **only audio** output is supported. Mic. does not work

%prep

# Kernel 6.4 Patch
perl -pi -e "s,\(THIS_MODULE\, ,,g" apple_bce.c
perl -pi -e "s,\(THIS_MODULE\, ,,g" audio/audio.c
perl -pi -e "s,\(THIS_MODULE\, ,,g" vhci/vhci.c
perl -pi -e "s,\$\(MAKE\),make CC=clang CXX=clang++ LD=ld.lld AR=llvm-ar NM=llvm-nm OBJCOPY=llvm-objcopy OBJSIZE=llvm-size STRIP=llvm-strip,g" Makefile

%build

%install
rm -rf %{buildroot}

# install dkms sources
mkdir -p %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}
cp -R * %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/
cat > %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/dkms.conf << EOF
PACKAGE_NAME=%{name}
PACKAGE_VERSION=%{version}-%{release}
CLEAN="make clean"
MAKE[0]="make CC=clang CXX=clang++ LD=ld.lld AR=llvm-ar NM=llvm-nm OBJCOPY=llvm-objcopy OBJSIZE=llvm-size STRIP=llvm-strip"
BUILT_MODULE_NAME[0]=${name}
DEST_MODULE_LOCATION[0]="/updates"
AUTOINSTALL="yes"
REMAKE_INITRD="yes"
EOF

%post
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %{name} -v %{version}-%{release}
if [ -z "$DURING_INSTALL" ] ; then
    /usr/sbin/dkms --rpm_safe_upgrade build -m %{name} -v %{version}-%{release} &&
    /usr/sbin/dkms --rpm_safe_upgrade install -m %{name} -v %{version}-%{release}
fi

%preun
# rmmod can fail
/sbin/rmmod %{kname} >/dev/null 2>&1 ||:
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{name} -v %{version}-%{release} --all || :

%posttrans
if [ -z "$DURING_INSTALL" ] ; then
    /sbin/rmmod %{kname} >/dev/null 2>&1 ||:
    /sbin/modprobe %{kname} >/dev/null 2>&1 ||:
fi

%clean
rm -rf %{buildroot}

%files
%doc lib/LICENSE.txt
%dir %{_usr}/src/%{name}-%{version}-%{release}
%{_usr}/src/%{name}-%{version}-%{release}/*
