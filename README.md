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
  1) Application takes the NSOT file as its input
 
  2) Use the neutron CLI commands (through python subprocess libarary) to perform:
  
     a) Creation of network: 
        
        neutron net-create <network_name> -f json
     
     b) Creation of subnet for the network:
     
        neutron subnet-create --name <subnet_name> <network_name> <subnet [192.168.10.0/24]> -f json"
     
     c) Creation of VMs:
     
        nova boot --flavor m1.tiny --image <vm_image_name> --min-count <vm_count> --nic net-id=<Netowrk_Id> <VM_Initial_Names>
     
     d) Creation of router (for inter and intra-communication):
     
        neutron router-create <router_name> -f json
     
     e) Setting the default gateway for router (for internet connection):
     
        neutron router-gateway-set <router_name> public
     
     f) Attaching the created subnet in point b with the router created in point d:
     
        neutron router-interface-add <router_id> <subnet_name>
     
     g) Creation of floating IP (based on number of VM created in point c):
     
        neutron floatingip-create public -f json
     
     h) Find the VM port created in point c and associate them with the floating IPs created in point g:
     
        neutron floatingip-associate <floating_ip_id> <vm_port_id>
     
     i) Creation of security rule:
     
        ICMP: openstack security group rule create --protocol icmp <default_security_group_id> -f json
        
        SSH:  openstack security group rule create --protocol tcp --dst-port 22:22 <default_security_group_id> -f json
    
##### Note: "-f json" option is used in most commands for easily parsing the data
     
### Docker BGP Automation

   4)	Automate spinning up and configuring a Quagga/FRR BGP router as a Docker container.
      a)	Automate its BGP configuration to peer with the SDN controller in the next objective.
   5)	Automate spinning up and configuring an SDN controller as another Docker container.
      a)	Automate its BGP speaker configuration to peer with Quagga/FRR.
  
#### High-level Overview:
  1) Application takes the NSOT file as its input

  2) Create the require template files.
  
     frr.j2 - For FRR routing docker
     
     bgp_conf.j2 - for Ryu SDN controller docker
   
  3) Now replace the dynamic fields in templates with the the given input in NSOT file and generate the new files
     
     For example:
     
     In frr.j2 template file: router bgp <local_as> 
     
     Replace local_as with the actual as number from the NSOT file
     
     Generate new file - frr.conf
  
  4) Attach the configuration file while running the docker
     
     Frrouting docker: docker run -v /home/frr.conf:/etc/frr/frr.conf -itd --privileged --name <frr_docker_name> <frr_image_file>
     
     Ryu docker: docker run -tid -v /home/ssh.py:/root/ryu/ryu/services/protocols/bgp/operator/ssh.py \
                            
                            -v /home/app.py:/root/ryu/ryu/services/protocols/bgp/application.py \
                            
                            -v /home/bgp_conf.py:/root/ryu/ryu/services/protocols/bgp/bgp_conf.py --name <ryu_docker_name> <ryu_image_file>
     
     Notes:
     -  In Docker container, the bgpd option needs to be enabled in /etc/frr/daemons file. After that, commit the docker container and create new image and use that image while         attaching thr frr.conf file to new frr docker instance. (bgpd process requires stop/start of docker container)
     -  In Ryu controller container, 
   
