"""example/test script for developing drench_sdk"""
import pytest
from drench_sdk.workflow import WorkFlow, TaxonomyError
from drench_sdk.transforms import BatchTransform, GlueTransform
from drench_sdk.taxonomy import Taxonomy

def test_tx_err():
    """main func"""
    with pytest.raises(TaxonomyError):
        workflow = WorkFlow(pool_id=1234)

        workflow.addTransform(
            BatchTransform(
                name='example-batch-flow',
                input_data={
                    'path':'s3://some_bucket/pool_id/job_id',
                    'taxonomy':Taxonomy(
                        format_type='csv',
                        fields=[
                            {'name':'name', 'field_type':'string'},
                            {'name':'id', 'field_type':'integer'}
                        ]
                        ),
                    },
                output_data={
                    'path':'s3://some_bucket/pool_id/job_id',
                    'taxonomy':Taxonomy(
                        format_type='csv',
                        fields=[
                            {'name':'name', 'field_type':'string'},
                            {'name':'id', 'field_type':'integer'}
                        ]
                        ),
                },
                job_queue='test-queue',
                job_definition='sap-job-execution',
                parameters={
                    'job': '$.params.job'
                },
                Next='example-glue-job',
                Start=True
            )
        )

        workflow.addTransform(
            GlueTransform(
                name='example-glue-job',
                input_data={
                    'path':'s3://some_bucket/pool_id/job_id',
                    'taxonomy':Taxonomy(
                        format_type='csv',
                        fields=[
                            {'name':'firm_name', 'field_type':'string'},
                            {'name':'id', 'field_type':'integer'}
                        ]
                        ),
                    },
                output_data={
                    'path':'s3://some_bucket/pool_id/job_id',
                    'taxonomy':Taxonomy(
                        format_type='csv',
                        fields=[
                            {'name':'name', 'field_type':'string'},
                            {'name':'id', 'field_type':'integer'}
                        ]
                        ),
                },
                Jobname='example-job-def',
                AllocatedCapacity=2
            )
        )

        workflow.toJson()
