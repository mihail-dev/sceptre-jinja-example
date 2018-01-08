from troposphere import Parameter, Ref, Output
from troposphere.s3 import BucketPolicy
from sceptre_template import SceptreTemplate


class SceptreResource(SceptreTemplate):

    def __init__(self, sceptre_user_data):
        super(SceptreResource, self).__init__()
        self.sceptre_user_data = sceptre_user_data
        self.add_parameters()
        self.add_bucket_policy()

    def add_parameters(self):
        self.bucket_name = self.template.add_parameter(Parameter(
            "BucketName",
            Description="The name of the bucket to which this policy is applied",
            Type="String",
        ))

    def add_bucket_policy(self):
        for policy_name, policy_properties in self.sceptre_user_data.iteritems():
            policy_properties.update({"Bucket": Ref(self.bucket_name)})
            bucket_policy = self.template.add_resource(BucketPolicy(policy_name, **policy_properties))
            self.template.add_output(Output(
                policy_name,
                Value=Ref(bucket_policy)
            ))


def sceptre_handler(sceptre_user_data):
    return SceptreResource(sceptre_user_data).template.to_json()
