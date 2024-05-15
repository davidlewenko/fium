from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_s3 as s3,
    CfnOutput
)
from constructs import Construct

class VideoSplitterStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)  # Make sure this is properly initialized first

        # Reference an existing S3 bucket
        bucket = s3.Bucket.from_bucket_name(self, "ExistingBucket", "fiumlandingvideodata")

        # Define the IAM role for the Lambda function
        lambda_role = iam.Role(self, "LambdaExecutionRole",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
                               ])

        # Add permissions to the role to access the existing S3 bucket
        bucket.grant_read_write(lambda_role)

        # Define the Lambda function
        docker_func = lambda_.DockerImageFunction(self, "DockerFunc",
                                                  code=lambda_.DockerImageCode.from_image_asset('image'),
                                                  memory_size=1024,
                                                  timeout=Duration.seconds(10),
                                                  architecture=lambda_.Architecture.ARM_64,
                                                  role=lambda_role  # Associate the defined role with the Lambda
                                                  )

        # Add function URL to access the function
        function_url = docker_func.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
            cors=lambda_.FunctionUrlCorsOptions(
                allowed_methods=[lambda_.HttpMethod.ALL],
                allowed_headers=["*"],
                allowed_origins=["*"]
            )
        )

        # Output the URL of the function
        CfnOutput(self, "FunctionUrlValue",
                  value=function_url.url
                  )
