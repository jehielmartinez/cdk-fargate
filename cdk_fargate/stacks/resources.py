from aws_cdk import (
    core as cdk,
    aws_ecs as ecs,
    aws_ec2 as ec2,
)

class Resources(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, vpc: ec2.IVpc, env_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ECS Cluster
        self._cluster = ecs.Cluster(
            self,
            f"{env_name}-cluster",
            vpc=vpc
        )

    @property
    def cluster(self) -> ecs.ICluster:
        return self._cluster
