from aws_cdk import (
    core as cdk,
    aws_ecr as ecr,
)

class Repositories(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # API Repository
        api_repo = ecr.Repository(
            self,
            'api-strapi-repo',
            repository_name='strapi-api',
        )

        # Repository Stack Output
        self._output = {
            'strapi-api': api_repo,
        }

    @property
    def output(self):
        return self._output