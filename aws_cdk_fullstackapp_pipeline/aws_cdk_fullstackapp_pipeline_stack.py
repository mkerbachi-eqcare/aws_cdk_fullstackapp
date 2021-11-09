from aws_cdk import (
    aws_s3 as s3,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    core as cdk
)

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class AwsCdkFullstackappPipelineStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)



        # Stage: Code Checkout

        github_checkout = codebuild.Project(
            self,
            "Checkout code",
            project_name="CheckoutCode",
            description="Checkout code from Github",
            source=codebuild.Source.git_hub(
                owner="mkerbachi-eqcare",
                repo="aws_cdk_fullstackapp",
                report_build_status=False,
                webhook=False,
                # webhook_filters=[codebuild.FilterGroup.in_event_of(
                #     codebuild.EventAction.PUSH).and_branch_is(branch_name="*")
                # ]
            ),
            build_spec=codebuild.BuildSpec.from_source_filename(filename="aws_cdk_fullstackapp_pipeline/pipeline/buildspec.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=False
            )
        )

        code_bucket = s3.Bucket(
            self,
            id="cdk-code-bucket",
            bucket_name="cdk-code-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        source_output = codepipeline.Artifact()

        cdk_code_s3sourceaction = codepipeline_actions.S3SourceAction(
            action_name="cdk_code_bucket_action",
            bucket=code_bucket,
            bucket_key="cdk_code.zip",
            output=source_output,
            trigger=codepipeline_actions.S3Trigger.EVENTS,
            variables_namespace="SourceCDKVariablesNamespace"
        )



        # Stage: Code build

        build_stage = codebuild.Project(
            self,
            "Build code",
            project_name="BuildCode",
            description="Code build",
            build_spec=codebuild.BuildSpec.from_source_filename(filename="aws_cdk_fullstackapp_pipeline/pipeline/build-buildspec.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=False
            )
        )

        cdk_code_codebuildaction = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=build_stage,
            input=source_output,
            variables_namespace="BuildCDKVariablesNamespace"
        )

        ############################
        # CodePipeline
        ############################

        pipeline = codepipeline.Pipeline(
            self,
            "CodePipeline",
            pipeline_name="FullStackApp_Pipeline",
            stages=[codepipeline.StageProps(
                stage_name="CodeCDK",
                actions=[cdk_code_s3sourceaction]
            ),
            codepipeline.StageProps(
                stage_name="Codebuild",
                actions=[cdk_code_codebuildaction]
            )]
        )