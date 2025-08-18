# openstack/client.py
import openstack

def get_openstack_connection():
    return openstack.connect(cloud='openstack')