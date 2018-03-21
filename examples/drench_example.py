workflow = Workflow(pool='some_pool_id')

workflow.addFlow(
    BatchFlow(
        name='example-batch-flow',
        in_taxonomy=Taxonomy(id=int, name=str),
        out_taxonomy=Taxonomy(name=str),
        job_queue='test-queue',
        job_definition='sap-job-execution',
        parameters={
            'job': '$.params.job'
        },
        next='SuccessSend'
        start=True
    )
)

workflow.addFlow(
    SNSFlow(
        name='SuccessSend',
        in_taxonomy=Taxonomy(name=str),
        out_taxonomy=Taxonomy(name=str),
        topic_arn=Resource.get_arn('sns', 'example_topic'),
        subject='Job succeeded.',
        message='Job succeeded.',
        end=True
    )
)

print(workflow.toJson())
