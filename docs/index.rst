=====================================================================
Funtoo Linux Network Configuration
=====================================================================

:keywords: linux, networking, funtoo, gentoo, Daniel Robbins, dhcpcd, Wi-Fi, 802.11, wireless, openresolv
:description: 

  This document explains how to configure your network settings by explaining
  the network configuration functionality available in Funtoo Linux. Also covered is
  ``dhcpcd 5.x``, Wi-Fi (IEEE 802.11) configuration, and the OpenResolv framework.

:author: drobbins
:contact: drobbins@funtoo.org
:copyright: funtoo
:language: English

Introduction
============

.. _Gentoo Linux: http://www.gentoo.org
.. _OpenRC: http://roy.marples.name/projects/openrc
.. role:: change

Funtoo Linux has its own core network configuration that differs somewhat from
upstream network configuration systems used in `Gentoo Linux`_ and `OpenRC`_.
Despite this difference, Funtoo Linux remains compatible with upstream `Gentoo
Linux`_ and `OpenRC`_. 

In this document, I will explain the unique additions and changes to the Funtoo
network configuration, why these changes were made, and how to use this system
to configure your network.

I'll also explain how to use ``dhcpcd 5.x`` for managing network interfaces on
DHCP-based networks, and will also cover *Wi-Fi* (IEEE 802.11) configuration
and the OpenResolv framework.

Funtoo network configuration is quite functional but is also something that I
periodically improve and enhance as Funtoo Linux progresses in its development.

.. Important:: There is no need to use netif.d templates. You can use simple scripts to set up network. See the examples in /usr/share/doc/funtoo-netscripts-\*/

A Gentle Introduction to Funtoo Network Configuration
=====================================================

Before I get into the technical details of configuring your network, it's
important to understand that Funtoo Linux has a number of different options
available to you for network configuration, with more likely to be added in the
future. Each approach is different and has its own strengths and weaknesses,
and this is, in my opinion, a good thing.

The Easy (Dynamic) Way
----------------------

When configuring your network, one option is to skip traditional network
configuration and simply rely on DHCP. This is by far the simplest method of
configuring your network.  If you are on a wired network, no other steps are
typically required beyond enabling a DHCP client, and Funtoo Linux includes
``dhcpcd 5.x`` by default.  To enable DHCP at system startup, you would
add ``dhcpcd`` to your default runlevel as follows::

        # rc-update add dhcpcd default
       
To enable DHCP immediately, you would follow the previous command with an
``rc`` command, which would start the ``dhcpcd`` client you just added::

        # rc

If you're on a wired network and have the necessary drivers in your kernel,
then this should get you going. For wireless networks, more steps are required
which will be covered later in this document. For now, it's important to note
that ``dhcpcd 5.x`` will manage *all* available network interfaces by default,
although this behavior can be changed by editing ``/etc/conf.d/dhcpcd``.

The Modular Way
---------------

DHCP isn't always an option, and for these situations, Funtoo Linux offers its
own modular, template-based network configuration system. This system offers a
lot of flexibility for configuring network interfaces, essentially serving as a
"network interface construction kit." This system can be used by itself, or
even combined with ``dhcpcd`` -- if you limit ``dhcpcd`` to only manage certain
network interfaces.

Here are the key components of the template-based network configuration system:

0) ``/etc/init.d/netif.lo`` -- An init script that configures the localhost
   interface.

1) ``/etc/netif.d`` -- This is a directory that contains various network
   configuration templates. Each of these templates is focused on configuring
   a particular type of network interface, such as a general static IP-based
   interface, a bridge interface, a bond interface, etc.

2) ``/etc/init.d/netif.tmpl`` -- This is the master init script for the
    template-based network configuration system. New interfaces are added
    to your system by creating **symbolic links** to this file in ``/etc/init.d``.
    
So, if you wanted to use this system to configure ``eth0`` with a static
IP address, you would create a ``netif.eth0`` symlink to ``netif.tmpl``
as follows::

        # cd /etc/init.d
        # ln -s netif.tmpl netif.eth0

Then, you would create an ``/etc/conf.d/netif.eth0`` configuration file
that would specify which template to use from the ``/etc/netif.d``
directory::

Then, you would define required and optional variables for the particular
template you are using. Here is a description of all currently-available
network templates. In our particular case, the ``/etc/conf.d/netif.eth0``
file may contain something like this::

        template="interface"
        ipaddr="10.0.1.200/24"
        gateway="10.0.1.1"
        nameservers="10.0.1.1 10.0.1.2"
        domain="funtoo.org"

When configuring your own static network interface, one of ``ipaddr`` or
``ipaddrs`` is required and should specify the IP address(es) to configure for
this interface, in "a.b.c.d/netmask" format. Optional parameters include
``gateway``, which defines a default gateway for your entire network, and if
set should specify the gateway's IP address. In addition, ``domain`` and
``nameservers`` (space-separated if more than one) can be used to specify DNS
information for this interface.

OpenResolv and resolv.conf
--------------------------

For the network configuration above, OpenResolv will be used to set DNS
information when the ``netif.eth0`` is brought up. The OpenResolv framework
will add entries to ``/etc/resolv.conf``, and will also handle removing these
entries when the interface is brought down. This way, ``/etc/resolv.conf``
should always contain current information and should not need to be manually
edited by the system administrator.

Network-Dependent Services
--------------------------

One important difference between Gentoo Linux and Funtoo Linux is that, by
default, network-dependent services only strictly depend on ``netif.lo``.  This
means that if a network service requires an interface to be up, such as
``samba`` requiring ``eth0``, then the system administrator must specify this
relationship by adding the following line to ``/etc/conf.d/samba``::

        rc_need="netif.eth0"

This will have the effect of ensuring that ``netif.eth0`` is started prior
to ``samba`` and that ``samba`` is stopped prior to stopping ``netif.eth0``.

Many network services, especially those that listen on all network intefaces,
don't need an ``rc_need`` line in order to function properly. Avoiding the
use of ``rc_need`` when required will optimize boot times and allow more
network services to remain available when network interfaces are brought up
and down by the system administrator.

Multiple Network Configurations
-------------------------------

It is common for laptop users to use DHCP most of the time, but
occasionally connect to network where a static network configuration
is required. This is a situation where one Funtoo Linux machine will
require **multiple** network configurations, and a mechanism will be
required to allow the user to switch between both configurations as
needed.

The recommended approach for doing this is to use multiple, stacked runlevels.
To do this, you will need to create two new runlevels which are children
of the ``default`` runlevel. This can be done like this::

        # install -d /etc/runlevels/static
        # install -d /etc/runlevels/dynamic

Two new runlevels, ``static`` and ``dynamic``, have now been created.
Now, we will make these runlevels children of the ``default`` runlevel
using the following commands::

        # rc-update --stack add default static
        # rc-update --stack add default dynamic

Now, the runlevels ``static`` and ``dynamic`` will consist of anything
in ``default`` **plus** any additional scripts you add to each new
runlevel.

To complete our multiple network configuration, we would now do something
like this::

        # rc-update add netif.eth0 static
        # rc-update add dhcpcd dynamic

If you need to run the same service with different configuration parameters
depending upon runlevel, then you'll be happy to know that you can specify
runlevel-specific conf.d files by appending a ``.runlevel`` suffix. In this
particular example, we could imagine a situation where we had two child
runlevels named ``home`` and ``work``::

        /etc/conf.d/netif.eth0.home
        /etc/conf.d/netif.eth0.work

Note that this feature works for all init scripts, not just network
configuration scripts. 

Wireless Configuration
======================

Wireless network configuration requires additional steps to the ones outlined
above.

For wireless networks, you will need to enable wireless extensions in
your kernel, the appropriate wireless modules, and emerge ``wireless-tools``::

        # emerge wireless-tools

I also recommend you ``emerge wpa_supplicant`` 0.6.9 or later, which includes
an OpenRC-compatible initscript that is compatible with Funtoo as well.
``wpa_supplicant`` implements modern WPA/WPA2 wireless link-layer encryption,
which is necessary for connecting to most modern password-protected wireless
networks.  After emerging, add to your default runlevel as follows::

        # rc-update add wpa_supplicant default

Many wireless adapters will now have everything they need to work. However,
if you have an Intel wireless adapter, then you may need to install the
proper microcode for your device in addition to ensuring that the proper Intel
Wireless kernel drivers are available. For my ``Intel Corporation PRO/Wireless
AGN [Shiloh] Network Connection``, I need to do the following::

        # emerge net-wireless/iwl5000-ucode

``udev`` (running by default) and the Linux kernel firmware loader support
(``CONFIG_FW_LOADER``) will automatically load the microcode when needed.

Note that Gentoo and Funtoo provide different versions of the Intel microcode
because the version you need will depend on the kernel you are using. For my
RHEL5-based kernel, I had emerge an older version of the microcode to match
what my kernel wireless driver was expecting by typing::

        # emerge =net-wireless/iwl5000-ucode-5.4.0.11

This installed this file ``iwlwifi-5000-1.ucode`` which was required by my
RHEL5-based kernel. Just typing ``emerge net-wireless-iwl5000-ucode`` installed
``iwlwifi-500-2.ucode``, which my kernel could not use. Before I had the
right version of the microcode, I saw an error like this when I viewed the
kernel messages by typing ``dmesg``::

        iwl5000: iwlwifi-5000-1.ucode firmware file req failed: Reason -2

This error message generally means "I can't find this file
*``iwlwifi-5000-1.ucode`` that I'm looking for in ``/lib/firmware``."* With the
proper firmware in place, then the wireless driver will be happy and
wpa-supplicant can then bring the wireless interface up.

802.11 Passphrases
------------------

The only remaining step is to use the ``wpa_passphrase`` utility to store
hashed keys (passwords) that ``wpa_supplicant`` can use to connect to your
favorite wireless networks. This is done as follows::

        # wpa_passphrase jims-netgear >> /etc/wpa_supplicant/wpa_supplicant.conf
        <enter your passphrase>

Now, when ``wpa_supplicant`` encounters an SSID of ``jims-netgear``, it will use
the password you entered to authenticate with this access point.

At this point, ensure that ``dhcpcd`` has been enabled in your current runlevel
and type ``rc`` to start everything up. ``wpa_supplicant`` should be able to
automatically associate with SSIDs in its config file, at which point ``dhcpcd``
will take over and acquire an IP address from a DHCP server. This should all
happen seamlessly. Use the ``iwconfig`` command to see if you have successfully
associated with an access point.

Other Network Configurations
============================

.. _funtoo-dev mailing list: http://groups.google.com/group/funtoo-dev

If you have a network configuration template that might be useful to others,
please post it to the `funtoo-dev mailing list`_ so we can review it and
possibly incorporate it into Funtoo.

