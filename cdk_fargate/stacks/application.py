from aws_cdk import (
    core as cdk,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as ecr,
    aws_ssm as ssm,
    aws_elasticloadbalancingv2 as elb
)

class Application(cdk.Stack):
    def __init__(
            self,
            scope: cdk.Construct,
            id: str,
            vpc: ec2.IVpc,
            application: str,
            env_name: str,
            cpu: int,
            memory_limit: int,
            port: int,
            repository: ecr.IRepository,
            cluster: ecs.ICluster,
            desired_count: int,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Image Tag Name
        image_tag_name = f"/{env_name}/{application}/image_tag"

        image_tag = ssm.StringParameter(
            self,
            f"{application}-image-tag-ssm-param",
            string_value='latest',
            parameter_name=image_tag_name,
            description=f"{application} Image Tag",
        )

        # Containerazed Application
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f"{env_name}-{application}-fargate-service",
            cluster=cluster,
            cpu=cpu,
            memory_limit_mib=memory_limit,
            task_subnets=ec2.SubnetSelection(subnet_group_name='Private'),
            desired_count=desired_count,
            protocol=elb.Protocol.HTTP,
            protocol_version=elb.ApplicationProtocolVersion.HTTP1,
            target_protocol=elb.Protocol.HTTP,
            task_image_options={
                'image': ecs.ContainerImage.from_ecr_repository(
                    repository=repository,
                    tag=image_tag.value_for_string_parameter(
                        self, image_tag_name),
                ),
                'container_port': port,
                'container_name': application,
                'enable_logging': True,
                'environment': {
                    # Temporal DB
                    'DATABASE_HOST': 'database.cuwya1t8wtqh.us-east-1.rds.amazonaws.com',
                    'DATABASE_PORT': '5432',
                    'DATABASE_PASSWORD': 'postgres',
                    'DATABASE_USERNAME': 'postgres',
                    'DATABASE_NAME': 'postgres',
                },
                'secrets': {}
            }
        )