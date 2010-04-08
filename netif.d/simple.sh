#!/bin/bash

start() {
	ebegin "$STARTD"
	ip link set $interface up || die "Couldn't bring $interface up"
	ezstart
	ezroute add; ezresolv add
	eend $?
}

stop() {
	ebegin "$STOPD"
	ezresolv del; ezroute del
	ip link set $interface down || die "Couldn't bring $interface down"
	eend $?
}

qipr() {
	ip route $*
	[ "$1" = "add" ] && [ $? -ne 0 ] && die "Couldn't set route: $*"
}


