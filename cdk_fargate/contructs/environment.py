from aws_cdk import (
    core as cdk,
)

from cdk_fargate.stacks.network import Network
from cdk_fargate.stacks.repositories import Repositories
from cdk_fargate.stacks.resources import Resources
from cdk_fargate.stacks.application import Application


class Environment(cdk.Construct):
    def __init__(
            self,
            scope: cdk.Construct,
            id: str,
            vpc_cidr: str,
            env_name: str,
            repositories: dict,
            **kwargs):
        super().__init__(scope, id, **kwargs)

        # Network
        network = Network(scope, id + 'Network', vpc_cidr=vpc_cidr)

        # Resources
        resources = Resources(
            scope, id + 'Resources',
            vpc=network.vpc,
            env_name=env_name
        )

        # Application
        application = Application(
            scope, id + 'Application',
            vpc=network.vpc,
            application='strapi-api',
            env_name=env_name,
            cpu=256,
            memory_limit=2048,
            port=3000,
            repository=repositories.output['strapi-api'],
            cluster=resources.cluster,
            desired_count=1
        )
