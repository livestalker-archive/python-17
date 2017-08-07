License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/3/
Source0:        otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-root
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel
Summary:  ...


%description
Weather Service

Git version: %{git_version} (branch: %{git_branch})

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%define __etcdir    /usr/local/etc
%define __logdir    /var/log/
%define __bindir    /usr/local/ip2w/
%define __systemddir	/usr/lib/systemd/system/

%prep
%setup -n otus-%{current_datetime}

%pre
getent passwd ip2w > /dev/null || useradd -r -d  %{__bindir} -s /sbin/nologin ip2w
exit 0

%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
# create directories
%{__mkdir} -p %{buildroot}/%{__etcdir}
%{__mkdir} -p %{buildroot}/%{__logdir}
%{__mkdir} -p %{buildroot}/%{__bindir}
%{__mkdir} -p %{buildroot}/%{__systemddir}

%{__install} -pD -m 644 %{name}.ini %{buildroot}/%{__etcdir}/%{name}.ini
%{__install} -pD -m 644 %{name}.py %{buildroot}/%{__bindir}/%{name}.py
%{__install} -pD -m 644 %{name}.service %{buildroot}/%{__systemddir}/%{name}.service

%post
%systemd_post %{name}.service
systemctl daemon-reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%{__etcdir}/*
%{__bindir}/*
%{__systemddir}/*

#cd hw5 && chown root:root ip2w.spec && ./buildrpm.sh ip2w.spec && chown 1000:1000 ip2w.spec && cp /root/rpm/RPMS/noarch/ip2w-0.0.1-1.noarch.rpm . && chown 1000:1000 ip2w-0.0.1-1.noarch.rpm