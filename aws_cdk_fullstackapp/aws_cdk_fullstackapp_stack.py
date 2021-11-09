from aws_cdk import (
    aws_ec2 as ec2,
    aws_dynamodb as dynamodb,
    aws_apigatewayv2 as apigwv2,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    # aws_cloudfront_origins as cloudfront_origins,
    core as cdk
)

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class AwsCdkFullstackappStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # VPC
        vpc = ec2.Vpc(
            self,
            "VpcTest",
            cidr="10.0.0.0/16"
        )


        ############
        # Backend
        ############


        # DynamoDB
        dynamo_db = dynamodb.Table(
            self,
            "TestDB",
            table_name="TestDB",
            partition_key=dynamodb.Attribute(name="item_name",type=dynamodb.AttributeType.STRING),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        #VPClink
        vpclink_sg = ec2.SecurityGroup(
            self,
            id="VpcLink-SG",
            vpc=vpc,
            security_group_name="VpcLinkSG",
            description="Description here"
        )

        vpclink_sg.add_egress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.all_tcp())

        vpc_link = apigwv2.VpcLink(
            self,
            "VpcLink",
            vpc=vpc,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            vpc_link_name="VpcLink"
        )

        #HttpAPI

        api = apigwv2.HttpApi(
            self,
            "APIGW",
            api_name="APIGW",
            description="HTTP API",
            create_default_stage=False
        )

        dft_stage = apigwv2.HttpStage(
            self,
            "DftStage",
            http_api=api,
            stage_name="$default",
            auto_deploy=True
        )


        ############
        # Front end
        ############

        site_bucket = s3.Bucket(
            self,
            id="cdn-bucket-mkerbachi",
            bucket_name="cdn-bucket-mkerbachi",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        log_bucket = s3.Bucket(
            self,
            id="cdn-log-bucket-mkerbachi",
            bucket_name="cdn-log-bucket-mkerbachi",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        cloudfront_src_cfg=cloudfront.SourceConfiguration(
            behaviors=[cloudfront.Behavior(is_default_behavior=True)],
            s3_origin_source=cloudfront.S3OriginConfig(
                s3_bucket_source=site_bucket,
                origin_access_identity=cloudfront.OriginAccessIdentity(self, "OAI", comment="Connects CF with S3")
            )
        )


        cdn = cloudfront.CloudFrontWebDistribution(
            self,
            "MyCDN",
            origin_configs=[cloudfront_src_cfg],
            comment="CDN by AWS Cloudfront",
            default_root_object="index.html",
            enabled=True,
            error_configurations=[cloudfront.CfnDistribution.CustomErrorResponseProperty(
                error_code=403,
                error_caching_min_ttl=3,
                response_code=200,
                response_page_path="/index.html"
            )],
            logging_config=cloudfront.LoggingConfiguration(
                bucket=log_bucket,
                include_cookies=True
            )
        )