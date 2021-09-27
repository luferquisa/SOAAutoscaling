#
# oci-list-instances-python version 1.0.
#
# Copyright (c) 2020 Oracle, Inc.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

import io
import json
from fdk import response

import oci

def handler(ctx, data: io.BytesIO=None):
    #Autenticacion contra OCI
    signer = oci.auth.signers.get_resource_principals_signer()
    #OCID del stack  que gestiona el SOA
    stackid ="ocid1.ormstack.oc1.iad.aaaaaaaazguq5itzsyswhymqpunry6fokqu3sid3vb2li5bfrkkscmvuxqja"
    #Se llama metodo 
    r = edit_stack(signer, stackid)
    return response.Response(
        ctx,
        response_data=r,
        headers={"Content-Type": "application/json"}
    )


    
def edit_stack(signer,stackid):

    resource_manager_client = oci.resource_manager.ResourceManagerClient(config = {}, signer=signer) 
    
    get_stack_response=resource_manager_client.get_stack(stack_id=stackid)
    
    variables = get_stack_response.data.variables
    
    node = variables['wls_scaleout_node_count'] 
    #El numero maximo de nodos es 3, solo se hace scale out si la cuenta es menor que 3
    if int(node) < 3:
        node = int(node) + 1
    #Se edita el stack
    variables['wls_scaleout_node_count'] = str(node)
    detalles = oci.resource_manager.models.UpdateStackDetails(
        display_name=get_stack_response.data.display_name,
        description=get_stack_response.data.description,
        config_source=oci.resource_manager.models.UpdateZipUploadConfigSourceDetails(
            config_source_type="ZIP_UPLOAD"),
        variables=variables,
        terraform_version=get_stack_response.data.terraform_version,
        freeform_tags=get_stack_response.data.freeform_tags,
        defined_tags=get_stack_response.data.defined_tags)
       
    update_stack_response = resource_manager_client.update_stack(
    stack_id=stackid,
    update_stack_details=detalles)
    #Se ejecuta el job
    create_job_response = resource_manager_client.create_job(
        create_job_details=oci.resource_manager.models.CreateJobDetails(
            stack_id=stackid,
            display_name="fromapi",
            operation="APPLY",
            job_operation_details=oci.resource_manager.models.CreateApplyJobOperationDetails(
                operation="APPLY",
                execution_plan_strategy="AUTO_APPROVED")))
    
    
    return create_job_response.data


