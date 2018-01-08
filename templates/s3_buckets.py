from troposphere import Ref, Output, GetAtt
from troposphere.s3 import Bucket, LifecycleConfiguration, LifecycleRule, LifecycleRuleTransition
from troposphere.s3 import CorsRules, CorsConfiguration, LoggingConfiguration, VersioningConfiguration
from sceptre_template import SceptreTemplate


class SceptreResource(SceptreTemplate):

    def __init__(self, sceptre_user_data):
        super(SceptreResource, self).__init__()
        self.sceptre_user_data = sceptre_user_data
        self.add_s3_buckets()

    def add_s3_buckets(self):
        for bucket_name, bucket_kwargs in self.sceptre_user_data.iteritems():
            if "BucketName" not in bucket_kwargs:
                bucket_kwargs.update({"BucketName": bucket_name})
            bucket_kwargs.update(self.tag_resource(bucket_kwargs.pop("Tags")))
            if "LifecycleConfiguration" in bucket_kwargs:
                bucket_kwargs.update(self.add_lifecycle_config(bucket_kwargs.pop("LifecycleConfiguration")))
            if "CorsConfiguration" in bucket_kwargs:
                bucket_kwargs.update(self.add_cors_config(bucket_kwargs.pop("CorsConfiguration")))
            if "LoggingConfiguration" in bucket_kwargs:
                logging_config = LoggingConfiguration(**bucket_kwargs.pop("LoggingConfiguration"))
                bucket_kwargs.update({"LoggingConfiguration": logging_config})
            if "VersioningConfiguration" in bucket_kwargs:
                versioning_config = VersioningConfiguration(**bucket_kwargs.pop("VersioningConfiguration"))
                bucket_kwargs.update({"VersioningConfiguration": versioning_config})
            # Finally create the bucket
            bucket = self.template.add_resource(Bucket(bucket_name, **bucket_kwargs))
            self.template.add_output(Output(
                bucket_name + "BucketName",
                Value=Ref(bucket)
            ))
            self.template.add_output(Output(
                bucket_name + "BucketArn",
                Value=GetAtt(bucket, "Arn")
            ))

    def add_lifecycle_config(self, configuration):
        lifecycle_rules = []
        for rule_kwargs in configuration:
            # Parse transitions if present in the rule definition
            if "Transitions" in rule_kwargs:
                transitions = []
                for transition in rule_kwargs.pop("Transitions"):
                    rule_transition = LifecycleRuleTransition(**transition)
                    transitions.append(rule_transition)
                rule_kwargs.update({"Transitions": transitions})
            lifecycle_rule = LifecycleRule(**rule_kwargs)
            lifecycle_rules.append(lifecycle_rule)
        lifecycle_config_kwargs = {
            "Rules": lifecycle_rules
        }
        lifecycle_config = LifecycleConfiguration(**lifecycle_config_kwargs)
        return {"LifecycleConfiguration": lifecycle_config}

    def add_cors_config(self, configuration):
        cors_rules = []
        for rule_kwargs in configuration:
            cors_rules.append(CorsRules(**rule_kwargs))
        cors_config = CorsConfiguration(**{"CorsRules": cors_rules})
        return {"CorsConfiguration": cors_config}

def sceptre_handler(sceptre_user_data):
    return SceptreResource(sceptre_user_data).template.to_json()
