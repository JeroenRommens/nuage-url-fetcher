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

## Example Output

	Jeroens-MacBook-Pro:nuage-url-fetcher jrommens$ python nuage_url_fetcher.py --vsd "10.167.1.60" --enterprise "vns0" --nsg-name "Test" 
	http://registration.nsg?data=eyJpbnN0YWxsZXIiOnsiZmlyc3ROYW1lIjoiZHVtbXkiLCJsYXN0TmFtZSI6ImR1bW15IiwibW9iaWxlTnVtYmVyIjpudWxsLCJpZCI6ImI1ZTg1NDM1LTg5ODctNGQxMS05OWFiLWRkMzMyZGY4NjhlZiIsImVtYWlsIjoiZHVtbXlAZHVtbXkuY29tIn0sInByb3h5RE5TTmFtZSI6InBvZHMtZXh0LmluZnIuZXUubnVhZ2VkZW1vLm5ldCIsImxvY2F0aW9uIjp7ImNvdW50cnkiOm51bGwsImFkZHJlc3MiOiIiLCJsb2NhbGl0eSI6bnVsbCwiaWQiOiJiYmQ5MjBlMS02ZDYxLTQ4MjQtYmQyYS1mOWU0YTAwYjRlYTkiLCJzdGF0ZSI6bnVsbH0sImJvb3RzdHJhcCI6eyJpZCI6IjY4NWFmNWEyLWZjOGItNGU1MC1iMDYxLWFiNDQxOWY4MjcxOCIsInN0YXR1cyI6Ik5PVElGSUNBVElPTl9BUFBfUkVRX0FDSyJ9LCJnYXRld2F5Ijp7InRwbU93bmVyIjoiIiwic3lzdGVtSUQiOiIxMzYuMTguMTE5LjIiLCJ1cGxpbmtzIjpbeyJuYW1lIjoicG9ydDEiLCJ2NCI6eyJtb2RlIjoiZGhjcCIsImluc3RhbGxlcm1hbmFnZWQiOmZhbHNlfX1dLCJlbnRlcnByaXNlIjoidm5zMCIsIm5hbWUiOiJUZXN0IiwiZGVzY3JpcHRpb24iOm51bGwsImlkIjoiMjU4NmU1MTEtYTVjNi00NjhhLWE3MjctMWMzNjUwYmFhYzU1IiwiZW50ZXJwcmlzZUlEIjoiOWQ4MWFhZjgtNzg0Mi00YTlhLTlkODAtYjNiOGVhZDMwMjQwIiwic3JrIjoiIiwic3ViamVjdEROIjoiVUlEPTI1ODZlNTExLWE1YzYtNDY4YS1hNzI3LTFjMzY1MGJhYWM1NSwgQ049VGVzdCwgTz12bnMwIn0sInVybCI6Imh0dHBzOi8vcHJveHktYm9vdHN0cmFwOjEyNDQzL251YWdlL2FwaS92NV8wL25zZ2F0ZXdheXMvMjU4NmU1MTEtYTVjNi00NjhhLWE3MjctMWMzNjUwYmFhYzU1L2Jvb3RzdHJhcGFjdGl2YXRpb25zIn0=