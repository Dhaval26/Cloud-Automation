# Cloud-Automation

The application created as part of this project performed following automation:

### OpenStack Automation
  1)	Automate the creation of multiple virtual networks (VNs) within the hypervisor and their connection to the public network.
  2)	Automate the creation of multiple VMs within the hypervisor-
      a)	Both single tenant (same VN) and multi-tenant (different VNs).
      b)	All VMs should be accessible from the host server and be able to access the Internet.
  3)  Automate the security groups and port security configuration to make intra-VN and inter-VN communication possible.

  Pre-requisite:
  
  Notes:
  

### Docker BGP Automation
   4)	Automate spinning up and configuring a Quagga/FRR BGP router as a Docker container.
      a)	Automate its BGP configuration to peer with the SDN controller in the next objective.
   5)	Automate spinning up and configuring an SDN controller as another Docker container.
      a)	Automate its BGP speaker configuration to peer with Quagga/FRR.
  
  Pre-requisite:
  
  Notes:
