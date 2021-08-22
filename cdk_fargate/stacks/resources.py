from aws_cdk import (
    core as cdk,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
)

class Resources(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, vpc: ec2.IVpc, env_name: str, username: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ECS Cluster
        self._cluster = ecs.Cluster(
            self,
            f"{env_name}-cluster",
            vpc=vpc
        )

        # RDS Postgres Database
        db_engine = rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_12_3)

        self.database = rds.DatabaseInstance(
            self, 'rds-postgres-database',
            credentials=rds.Credentials.from_generated_secret(username, exclude_characters='''%"'()*+,./:;=?@&[\]_`{|}~'''),
            engine=db_engine,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_group_name='Data'),
            multi_az=True if env_name == 'prod' else False,
        )

        # Security Group
        self.database.connections.allow_default_port_from(
            other=ec2.Peer.ipv4(vpc.vpc_cidr_block)
        )

    @property
    def cluster(self) -> ecs.ICluster:
        return self._cluster

    @property
    def rds_database(self) -> rds.IDatabaseInstance:
        return self.database
        
    @property
    def rds_database_connection(self) -> str:
        return self.database.instance_endpoint.socket_address

    @property
    def rds_database_hostname(self) -> str:
        return self.database.instance_endpoint.hostname

    @property
    def database_secrets(self) -> secretsmanager.ISecret:
        return self.database.secret