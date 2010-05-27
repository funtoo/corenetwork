#!/sbin/runscript

domain=${domain:-$DOM}
if [ -n "$IP" ]
then
	ipaddr=$IP/$NM
fi
netmask=${netmask:-$NM}
slaves=${slaves:-$SLAVES}
mtu=${mtu:-$MTU}
nameservers="${nameservers:-$NS1 $NS2}"
gateway=${gateway:-$GW}

ezdns() {
	# This function generates a resolv.conf entry, which ezresolv() passes to resolvconf
	[ -n "$domain" ] && echo "domain $domain"
	for ns in $nameservers
	do
		echo "nameserver $ns"
	done
}

ezresolv() {
	# This function calls resolvconf (openresolv) with the correct resolv.conf passed as a here-file
	[ -z "`ezdns`" ] && return
	if [ "$1" = "add" ]; then
		resolvconf -a $interface << EOF || die "Problem adding DNS info for $interface"
`ezdns`
EOF
	else
		resolvconf -d $interface
	fi
}

ezroute() {
	if [ "$gateway" = "default" ]
	then
		qipr $1 default dev $interface
	elif [ -n "$gateway" ]
	then
		qipr $1 default via $gateway
	fi
}

qipr() {
	ip route $*
	[ "$1" = "add" ] && [ $? -ne 0 ] && die "Couldn't set route: $*"
}
