# Cloud-Automation

The application created as part of this project is performing following automations:

#### Note: Network Source of Truth (NSOT) files are used in the application.

### OpenStack Automation
  1)	Automate the creation of multiple virtual networks (VNs) within the hypervisor and their connection to the public network.
  
  2)	Automate the creation of multiple VMs within the hypervisor-
  
      a)	Both single tenant (same VN) and multi-tenant (different VNs).
      
      b)	All VMs should be accessible from the host server and be able to access the Internet.
      
  3)  Automate the security groups and port security configuration to make intra-VN and inter-VN communication possible.

#### High-level Overview:

Application takes the NSOT file as its input and use the neutron and openstack CLI commands (using python subprocess library) to create the necessary networks/VMs/routers/floating IPs/security groups in the project. 

Script execution with the commands is shown here: [Openstack-Automation-Execution](Script-Execution/OpenStack-Automation/README.md)
 
 
 ### Docker BGP Automation

   4)	Automate spinning up and configuring a Quagga/FRR BGP router as a Docker container.
   
      a)	Automate its BGP configuration to peer with the SDN controller in the next objective.
      
   5)	Automate spinning up and configuring an SDN controller as another Docker container.
   
      a)	Automate its BGP speaker configuration to peer with Quagga/FRR.
  
#### High-level Overview:

Application takes the NSOT file as its input and create the configuration files based on templates files for the Ryu controller and FRR routing containers. After that, the configuration files are attached as volume to the docker container and verify the BGP peering.

Script execution with the commands is shown here: [Docker-Automation-Execution](Script-Execution/Docker-Automation/README.md)
