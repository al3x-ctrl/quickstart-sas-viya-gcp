""" Creates the viya spre VM """

""" Startup script for Viya spre """
spre_startup_script = '''#! /bin/bash
# Setting up environment
export COMMON_CODE_COMMIT="{common_code_commit}"
export NFS_SERVER="{deployment}-ansible-controller"
export HOST=$(hostname)
# Set SELinux to Permissive on Viya nodes
# In Viya 3.5, Viya-ark now validates that SELinux is *not* enforced.
setenforce 0
sed -i.bak -e 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
# Installing dependencies
yum -y install git
# Getting quick start scripts
git clone https://github.com/al3x-ctrl/quickstart-sas-viya-common-gcp /tmp/common
pushd /tmp/common
#git checkout $COMMON_CODE_COMMIT -b $COMMON_CODE_COMMIT
# Clean up GitHub identifier files
rm -rf .git*
popd
# Bootstrapping all SAS VM
/bin/su sasinstall -c '/tmp/common/scripts/sasnodes_prereqs.sh'
# VIRK requires GID 1001 to be free
groupmod -g 2001 sasinstall
# Final system update
yum -y update
# Moving yum cache to /opt/sas where there is more room to retrieve sas viya repo
while [[ ! -d /opt/sas ]];
do
  sleep 2
done
sed -i '/cachedir/s/var/opt\/sas/' /etc/yum.conf
'''

def GenerateConfig(context):
    """ Retrieve variable values from the context """
    common_code_commit = context.properties['CommonCodeCommit']
    source_image = context.properties['SourceImage']
    spre_machinetype = context.properties['SpreMachineType']
    deployment = context.env['deployment']
    zone = context.properties['Zone']
    ssh_key = context.properties['SSHPublicKey']
    boot_disk = context.properties['BootDisk']
    sashome_disk = context.properties['SASHomeDisk']
    nr_of_disks = context.properties['SpreDisks']
    saswork_disk = context.properties['SpreDiskSize']

    """ Define the resources for the VMs """
   
    if nr_of_disks == 2:
     resources = [
        {
            'name': "{}-spre".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, spre_machinetype),
                'hostname': "spre.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                   'disks': [
                    {
                        'deviceName': 'boot',
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk),
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-spre-home".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
                            'description': "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName': 'saswork-1',
                        'type': "SCRATCH",
                        'interface': "NVME", 
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-1"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-2',
                        'type': "SCRATCH",
                        'boot': False,
                        'interface': "NVME",
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-2"
                        }
                    }

                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script', 'value': spre_startup_script.format(common_code_commit=common_code_commit, deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }

            }
        }
    ]
  
    if nr_of_disks == 3:
     resources = [
        {
            'name': "{}-spre".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, spre_machinetype),
                'hostname': "spre.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                   'disks': [
                    {
                        'deviceName': 'boot',
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk),
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-spre-home".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
                            'description': "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName': 'saswork-1',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-1"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-2',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-2"
                        }
                    },
                    {
                        'deviceName': 'saswork-3',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-3"
                        }
                    }

                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script', 'value': spre_startup_script.format(common_code_commit=common_code_commit, deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }

            }
        }
    ]

    if nr_of_disks == 4:
     resources = [
        {
            'name': "{}-spre".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, spre_machinetype),
                'hostname': "spre.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                   'disks': [
                    {
                        'deviceName': 'boot',
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk),
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-spre-home".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
                            'description': "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName': 'saswork-1',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-1"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-2',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-2"
                        }
                    },
                    {
                        'deviceName': 'saswork-3',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-3"
                        }
                    },
                    {
                        'deviceName': 'saswork-4',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-4"
                        }
                    }

                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script', 'value': spre_startup_script.format(common_code_commit=common_code_commit, deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }

            }
        }
    ]

    if nr_of_disks == 5:
     resources = [
        {
            'name': "{}-spre".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, spre_machinetype),
                'hostname': "spre.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                   'disks': [
                    {
                        'deviceName': 'boot',
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk),
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-spre-home".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
                            'description': "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName': 'saswork-1',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-1"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-2',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-2"
                        }
                    },
                    {
                        'deviceName': 'saswork-3',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-3"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-4',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-4"
                        }
                    },
                    {
                        'deviceName': 'saswork-5',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-5"
                        }
                    }
                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script', 'value': spre_startup_script.format(common_code_commit=common_code_commit, deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }

            }
        }
    ]

    if nr_of_disks == 6:
     resources = [
        {
            'name': "{}-spre".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, spre_machinetype),
                'hostname': "spre.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                   'disks': [
                    {
                        'deviceName': 'boot',
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk),
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-spre-home".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
                            'description': "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName': 'saswork-1',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-1"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-2',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-2"
                        }
                    },
                    {
                        'deviceName': 'saswork-3',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-3"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-4',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-4"
                        }
                    },
                    {
                        'deviceName': 'saswork-5',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-5"
                        }
                    },
                    {
                        'deviceName': 'saswork-6',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-6"
                        }
                    }
                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script', 'value': spre_startup_script.format(common_code_commit=common_code_commit, deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }

            }
        }
    ]
  
    if nr_of_disks == 7:
     resources = [
        {
            'name': "{}-spre".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, spre_machinetype),
                'hostname': "spre.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                   'disks': [
                    {
                        'deviceName': 'boot',
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk),
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-spre-home".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
                            'description': "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName': 'saswork-1',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-1"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-2',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-2"
                        }
                    },
                    {
                        'deviceName': 'saswork-3',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-3"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-4',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-4"
                        }
                    },
                    {
                        'deviceName': 'saswork-5',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-5"
                        }
                    },
                    {
                        'deviceName': 'saswork-6',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-6"
                        }
                    },
                    {
                        'deviceName': 'saswork-7',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-7"
                        }
                    }

                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script', 'value': spre_startup_script.format(common_code_commit=common_code_commit, deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }

            }
        }
    ]

    if nr_of_disks == 8:
     resources = [
        {
            'name': "{}-spre".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, spre_machinetype),
                'hostname': "spre.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                   'disks': [
                    {
                        'deviceName': 'boot',
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk),
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-spre-home".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
                            'description': "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName': 'saswork-1',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-1"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-2',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-2"
                        }
                    },
                    {
                        'deviceName': 'saswork-3',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-3"
                        }
                    }, 
                    {
                        'deviceName': 'saswork-4',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-4"
                        }
                    },
                    {
                        'deviceName': 'saswork-5',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-5"
                        }
                    },
                    {
                        'deviceName': 'saswork-6',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-6"
                        }
                    },
                    {
                        'deviceName': 'saswork-7',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-7"
                        }
                    },
                    {
                        'deviceName': 'saswork-8',
                        'type': "SCRATCH",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskSizeGb': "375",
                            'diskType': "zones/{}/diskTypes/local-ssd".format(zone),
                            'description': "sas-work-8"
                        }
                    }

                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script', 'value': spre_startup_script.format(common_code_commit=common_code_commit, deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }

            }
        }
    ]
    
    return {'resources': resources}
