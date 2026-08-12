import json
import boto3

def start_sm_execution(state_machine_arn, params):
    sm = boto3.client('stepfunctions')
    response = sm.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(params)
    )
    return response
