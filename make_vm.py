#!/bin/python
#######################################
##	WargameInABox
##	Automated VM Creation
##  written by obxhokie
#######################################

import libvert
import sys

# Get domain name
domname = sys.argv[1]
hostname = sys.argv[2]

# Create a connection to the hypervisor
#conn = libvert.openReadOnly(None)
conn = libvert.openReadOnly(dom)
if conn = None:
	print 'Failed to open connection to the hypervisor'
	sys.exit(1)

try:
	dom0 = conn.lookupByName("Domain-0")
except:
	print 'Failed to find the main domain'
	sys.exit(1)

print "Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType())
print dom0.info()
