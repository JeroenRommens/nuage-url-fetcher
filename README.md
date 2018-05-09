# nuage-url-fetcher

**NOTE: This package is considered Alpha quality.

## Overview

This is a Python script which can be used to retrieve an activation URL for a specific NSG. The script uses the Python VSPK and an AMQP Client to retrieve all information from the VSD.

## Prerequisites

This script can be run from any host as long as the following prerequesites are met:

1. Python VSPK package is installed (You can install with "pip install vspk")
1. Install QPID Proton for Python (You can install with "pip install python-qpid-proton")
1. There is IP connectivity between the host that will run the script and the VSD for ports 8443 and 5672

## Running the script

	python nuage_url_fetcher.py --vsd "10.167.1.60" --enterprise "vns0" --nsg-name "nsg-522-001"

The login used to access the VSD can be changed in at the top of the script by editing the following fields:

	username = "jmsclient"
	password = "jmsclient"
	login_enterprise = "csp"