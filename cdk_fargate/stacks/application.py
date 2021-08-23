import os
from aws_cdk import (
    core as cdk,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_route53 as route53,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elb,
    aws_secretsmanager as secretsmanager,
    aws_certificatemanager as certificatemanager,
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
            database_secrets: secretsmanager.ISecret,
            environment_variables: dict,
            subdomain: str,
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

        # Import Route53 Hosted Zone
        hosted_zone = route53.PublicHostedZone.from_hosted_zone_attributes(self, f'hosted-zone',
            hosted_zone_id=os.getenv('HOSTED_ZONE_ID'),
            zone_name=os.getenv('HOSTED_ZONE_NAME')
        )

        # Import Certificate
        certificate = certificatemanager.Certificate.from_certificate_arn(self, 'Certificate',
            certificate_arn=os.getenv('CERTIFICATE_ARN')
        )

        # Containerazed Application
        fargate_alb_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f'{env_name}-{application}-fargate-service',
            cluster=cluster,
            cpu=cpu,
            memory_limit_mib=memory_limit,
            task_subnets=ec2.SubnetSelection(subnet_group_name='Private'),
            desired_count=desired_count,
            protocol=elb.Protocol.HTTPS,
            certificate=certificate,
            domain_name=f'{subdomain}.{hosted_zone.zone_name}',
            domain_zone=hosted_zone,
            redirect_http=True,
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
                'environment': environment_variables,
                'secrets': {
                    'DATABASE_HOST': ecs.Secret.from_secrets_manager(database_secrets, 'host'),
                    'DATABASE_PORT': ecs.Secret.from_secrets_manager(database_secrets, 'port'),
                    'DATABASE_PASSWORD': ecs.Secret.from_secrets_manager(database_secrets, 'password'),
                    'DATABASE_USERNAME': ecs.Secret.from_secrets_manager(database_secrets, 'username'),
                },
            }
        )