from aws_cdk import (
    core as cdk,
)

from cdk_fargate.contructs.environment import Environment
from cdk_fargate.stacks.repositories import Repositories


class USEast1(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        environ=cdk.Environment(account='022508203523',region='us-east-1')
        super().__init__(scope, id, **{'env':environ, **kwargs})
    

        # Repositories
        repositories = Repositories(scope, 'Repositories')

        # Development Env
        Environment(scope, 'DevEnv', vpc_cidr='10.0.0.0/16', env_name='dev', repositories=repositories)

        # Production Env
        #Environment(scope, 'ProdEnv', vpc_cidr='10.0.0.0/16', env='prod')