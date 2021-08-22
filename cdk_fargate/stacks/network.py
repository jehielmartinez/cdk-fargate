from aws_cdk import (
    core as cdk,
    aws_ec2 as ec2,
)


class Network(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, vpc_cidr: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        self._vpc = ec2.Vpc(
            self, id + 'Vpc',
            cidr=vpc_cidr,
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='Public',
                    subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(
                    name='Private',
                    subnet_type=ec2.SubnetType.PRIVATE),
                ec2.SubnetConfiguration(
                    name='Data',
                    subnet_type=ec2.SubnetType.ISOLATED),
            ],
        )

    @property
    def vpc(self) -> ec2.IVpc:
        return self._vpc