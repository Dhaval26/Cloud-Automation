try:
    import subprocess
    from subprocess import Popen
    import json
    import time
    import csv
except ImportError as e:
    print (e)

def Openstack_Automation(l):
    flag = 0
    for d in l:
        print (d)
        try:
            print ("Creating the network \n")
            network_name = d['network']
            net_create_cmd = "neutron net-create " + network_name + " -f json"
            print (net_create_cmd)
            p = Popen(net_create_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, errors = p.communicate()

            nw_op = json.loads(output)
            nw_op_id = nw_op["id"]
            print ("Network is created with id " + nw_op_id + "\n")

        except Exception as e:
            print (e)

        try:
            print ("Creating the subnet \n")
            subnet_name = "_".join(d['subnet'].split(".")[:3])
            subnet = d['subnet']
            nw_3oct = ".".join(d['subnet'].split(".")[:3])
            dhcp_serverip = ".".join(d['subnet'].split(".")[:3]) + ".2"
            ext_rtrip = ".".join(d['subnet'].split(".")[:3]) + ".1"
            subnet_create_cmd = "neutron subnet-create --name " + subnet_name + " " + network_name + " " + subnet + " -f json"
            print (subnet_create_cmd)
            p = Popen(subnet_create_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, errors = p.communicate()

            subnet_op = json.loads(output)
            subnet_op_id = subnet_op["id"]
            print ("Subnet is created with id " + subnet_op_id + "\n")

        except Exception as e:
            print (e)

        try:
            print ("Booting up the VMs \n")
            vm_img = d['vm_img']
            vm_count = d['vm_count']
            vm_boot_cmd = "nova boot --flavor m1.tiny --image " + vm_img + " --min-count " + vm_count + " --nic net-id=" + nw_op_id + " " + network_name.lower() + "boxes"
            print (vm_boot_cmd)
            p = Popen(vm_boot_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, errors = p.communicate()
            print (output)
            print (errors)
            print ("VMs are booting up \n")
            time.sleep(10)

        except Exception as e:
            print (e)

        if d['inter-vn'] == "Y" and flag == 0:
            try:
                print ("Inter-VN communication is required. Hence creating the router \n")
                rtr_create_cmd = "neutron router-create EXT_VR -f json"
                print (rtr_create_cmd)
                p = Popen(rtr_create_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, errors = p.communicate()

                rtr_op = json.loads(output)
                rtr_op_id = rtr_op["id"]
                print ("Router is created with id " + rtr_op_id + "\n")

            except Exception as e:
                print (e)
        else:
            print ("Intra-VN connection is not required for the hosts")

        if d['internet'] == "Y" and flag == 0:

            try:
                print ("Internet is required. Hence setting the default gateway for router \n")
                rtr_gw_cmd = "neutron router-gateway-set EXT_VR public"
                print (rtr_create_cmd)
                p = Popen(rtr_gw_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, errors = p.communicate()

                print ("Default gateway is set for router \n")

            except Exception as e:
                print (e)

        else:
            print ("Internet connection is not required for the hosts")

        try:
            print ("Attaching the created network with router")
            rtr_attach_cmd = "neutron router-interface-add " +  rtr_op_id + " " + subnet_name
            print (rtr_attach_cmd)
            p = Popen(rtr_attach_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, errors = p.communicate()

            print ("The created network attached with the external router \n")

            flag = 1

        except Exception as e:
            print (e)

        ip_list = []
        for i in range(int(vm_count)):
            try:
                print ("Creating floating IP \n")
                fip_create_cmd = "neutron floatingip-create public -f json"
                print (fip_create_cmd)
                p = Popen(fip_create_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, errors = p.communicate()

                fip_op = json.loads(output)
                fip_op_id = fip_op["id"]
                print ("Floating IP is created with id " + fip_op_id + "\n")

            except Exception as e:
                print (e)

            try:
                print ("finding the VM port id \n")
                find_vm_port = "neutron port-list -c id -c fixed_ips -f json"
                print (find_vm_port)
                p1 = Popen(find_vm_port, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, errors = p1.communicate()

                find_vm_op = json.loads(output)
                for i in find_vm_op:
                    for j in i['fixed_ips']:
                        if nw_3oct in j['ip_address'] and dhcp_serverip not in j['ip_address'] and ext_rtrip not in j['ip_address'] and j['ip_address'] not in ip_list:
                            vm_port_id = i['id']
                            print (vm_port_id)
                            ip_list.append(j['ip_address'])
                            print (ip_list)

                            print ("Attaching floating IP \n")
                            fip_attach_cmd = "neutron floatingip-associate " + fip_op_id + " " + vm_port_id
                            p2 = Popen(fip_attach_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                            output, errors = p2.communicate()
                            print (output)
                            print (errors)

                            print ("Associated floating ip with VM port id \n")

            except Exception as e:
                print (e)

        if d['icmp_secgrp'] == "Y" and d['ssh_secgrp'] == "Y":
            try:
                print ("Applying ICMP rule \n")
                icmp_cmd = "openstack security group rule create --protocol icmp 6970097f-4d73-48d8-a2f7-001e4400a350 -f json"
                p = Popen(icmp_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, errors = p.communicate()
                print (output)
                print (errors)
                print ("ICMP rule applied into default security group \n")

                print ("Applying SSH rule \n")
                ssh_cmd = "openstack security group rule create --protocol tcp --dst-port 22:22 6970097f-4d73-48d8-a2f7-001e4400a350 -f json"
                p = Popen(ssh_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, errors = p.communicate()
                print (output)
                print (errors)
                print ("SSH rule applied into default security group \n")

            except Exception as e:
                print (e)
        else:
            print ("Security rules are either implemented or not required")

def Docker_BGP_Automation(l):

    # Preparing frr.conf file for FRR routing instance and bgp_conf.py file for Ryu controller
    # based on NSOT file
    for d in l:
        container_type = d['container_type']
        if container_type == "FRR":
            local_as = d['local_as']
            remote_as = d['remote_as']
            neighbor_ip = d['neighbor_ip']

            with open('frr.j2', 'r') as file :
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace('{{local_as}}',local_as)
            filedata = filedata.replace('{{remote_as}}',remote_as)
            filedata = filedata.replace('{{neighbor_ip}}',neighbor_ip)

            # Write the file out again
            with open('frr.conf', 'w') as file:
                file.write(filedata)

            print ("BGP configuration file created for FRR routing docker")

            home_dir = "/home/dhaval/"
            frr_conf_file = "frr.conf"
            frr_docker_name = "frr_instance"
            frr_image_file = "frr_new"

            print ("Attaching BGP configuration on FRR routing docker")

            frr_bgp_cmd = "docker run -v " + home_dir + frr_conf_file + ":/etc/frr/frr.conf -itd --privileged --name " + frr_docker_name + " " + frr_image_file
            print (frr_bgp_cmd)
            p = Popen(frr_bgp_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, errors = p.communicate()
            print (output)
            print ("Docker container - frr_instance is created with id {}".format(output))

        else:
            local_as = d['local_as']
            remote_as = d['remote_as']
            neighbor_ip = "'" + d['neighbor_ip'] + "'"

            with open('bgp_conf.j2', 'r') as file :
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace('{{local_as}}',local_as)
            filedata = filedata.replace('{{remote_as}}',remote_as)
            filedata = filedata.replace('{{neighbor_ip}}',neighbor_ip)

            # Write the file out again
            with open('bgp_conf.py', 'w') as file:
                file.write(filedata)

            print ("BGP configuration file created for Ryu controller docker")

            home_dir = "/home/dhaval/"
            ryu_bgp_conf = "bgp_conf.py"
            ssh_conf = "ssh_sample.py"
            app_py = "app.py"
            ryu_docker_name = "ryu_bgp_new"
            ryu_image_file = "osrg/ryu"

            print ("Attaching BGP configuration on Ryu controller docker")
            ryu_bgp_cmd = "docker run -tid -v " + home_dir + ssh_conf + ":/root/ryu/ryu/services/protocols/bgp/operator/ssh.py" + \
                            " -v " + home_dir + app_py + ":/root/ryu/ryu/services/protocols/bgp/application.py " + \
                            " -v " + home_dir + ryu_bgp_conf + ":/root/ryu/ryu/services/protocols/bgp/bgp_conf.py " + " --name " + ryu_docker_name + " " + ryu_image_file
            print (ryu_bgp_cmd)
            p1 = Popen(ryu_bgp_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, errors = p1.communicate()
            print ("Docker container - ryu_bgp_new is created with id {}".format(output))

            time.sleep(5)

    print ("######## RYU Controller BGP APP output ########")
    ryu_bgp_run_cmd = "docker exec -it " + ryu_docker_name + " ryu-manager ./ryu/ryu/services/protocols/bgp/application.py --bgp-app-config-file ryu/ryu/services/protocols/bgp/bgp_conf.py"
    print (ryu_bgp_run_cmd)
    p2 = Popen(ryu_bgp_run_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, errors = p2.communicate()
    print (output)

    time.sleep(2)

    print ("######## FRR routing docker output ########")
    frr_run_cmd = 'docker exec -it ' + frr_docker_name + ' vtysh -c "show ip bgp summary"'
    print (frr_run_cmd)
    p3 = Popen(frr_run_cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, errors = p3.communicate()
    print (output)

if __name__ == "__main__":

    # Openstack Automation
    openstack_nsot_file = "Openstack_NSOT.csv"
    l1 = []
    try:
        with open (openstack_nsot_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for line in csv_reader:
                d = {}
                d['network'] = line[0]
                d['subnet'] = line[1]
                d['vm_img'] = line[2]
                d['vm_count'] = line[3]
                d['inter-vn'] = line[4]
                d['internet'] = line[5]
                d['icmp_secgrp'] = line[6]
                d['ssh_secgrp'] = line[7]
                l1.append(d)

    except IOError as e:
        print ("Unable to open file")

    Openstack_Automation(l1)

    # Docker Automation
    docker_bgp_nsot_file = "Docker_BGP_NSOT.csv"
    l2 = []
    try:
        with open (docker_bgp_nsot_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for line in csv_reader:
                d = {}
                d['container_type'] = line[0]
                d['local_as'] = line[1]
                d['neighbor_ip'] = line[2]
                d['remote_as'] = line[3]
                l2.append(d)

    except IOError as e:
        print ("Unable to open file")

    Docker_BGP_Automation(l2)
