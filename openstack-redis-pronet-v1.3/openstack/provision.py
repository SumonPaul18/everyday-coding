# openstack/provision.py
from openstack.client import get_openstack_connection
from models.user import db, User

def create_openstack_resources(user):
    conn = get_openstack_connection()
    try:
        project_name = f"user_{user.id}"
        project = conn.identity.create_project(name=project_name, domain_id="default")
        os_user = conn.identity.create_user(
            name=user.name or user.email.split('@')[0],
            email=user.email,
            password=os.urandom(12).hex(),
            domain_id="default",
            default_project=project.id
        )
        member_role = conn.identity.find_role("member")
        conn.identity.assign_role_to_user_on_project(project.id, os_user.id, member_role.id)

        network = conn.network.create_network(name=f"{project_name}-net", project_id=project.id)
        subnet = conn.network.create_subnet(
            name=f"{project_name}-subnet",
            network_id=network.id,
            ip_version=4,
            cidr="10.0.0.0/24",
            gateway_ip="10.0.0.1",
            project_id=project.id
        )
        router = conn.network.create_router(
            name=f"{project_name}-router",
            external_gateway_info={"network_id": "provider_net"}
        )
        conn.network.add_interface_to_router(router.id, subnet_id=subnet.id)

        user.openstack_project_id = project.id
        user.openstack_user_id = os_user.id
        user.openstack_network_id = network.id
        user.openstack_subnet_id = subnet.id
        user.openstack_router_id = router.id
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e