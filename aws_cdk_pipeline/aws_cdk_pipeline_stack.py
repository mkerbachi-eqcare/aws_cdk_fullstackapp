from aws_cdk import (
    aws_codebuild as codebuild,
    core as cdk
)

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class AwsCdkPipelineStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)



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
            build_spec=codebuild.BuildSpec.from_source_filename(filename="pipeline/buildspec.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=False
            )
        )