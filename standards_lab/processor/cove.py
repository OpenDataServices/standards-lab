from libcove.lib.common import (
    common_checks_context,
    get_additional_codelist_values,
    SchemaJsonMixin,
)

from decimal import Decimal
from urllib.parse import urljoin
import json
import os

import django_rq
from rq.job import Job
from rq.exceptions import NoSuchJobError


class UnfinishedJobExistsError(Exception):
    pass


def process_start_cove(project):
    job_id = project["name"] + "_cove_results"
    try:
        job = Job.fetch(job_id, connection=django_rq.get_connection())
        status = job.get_status()
        if status not in ["finished", "failed"]:
            raise UnfinishedJobExistsError(f"Job exists, and status is '{status}', so not queuing a new job.")
    except NoSuchJobError:
        pass

    context = {"file_type": "json"}
    # The directory where the resulting validation_errors-3.json is put
    # Currently this doesn't support multiple data files, because each run will
    # override the same file in this directory
    upload_dir = project["path"]
    # Assume the first schema file is the root
    # TODO issue for ui for this
    schema_name = project["schemaFiles"][0]

    print(project, flush=True)

    schema_obj = SchemaJsonMixin()

    schema_obj.schema_host = os.path.join(project["path"], "")
    # These are needed for flatten-tool:
    # schema_obj.schema_name = schema_name
    # schema_obj.schema_url = urljoin(schema_obj.schema_host, schema_obj.schema_name)
    schema_obj.pkg_schema_name = schema_name
    schema_obj.pkg_schema_url = urljoin(
        schema_obj.schema_host, schema_obj.pkg_schema_name
    )
    print(schema_obj.pkg_schema_url, flush=True)

    for data_file in project["dataFiles"]:
        with open(os.path.join(project["path"], data_file)) as fp:
            json_data = json.load(fp, parse_float=Decimal)

            job = django_rq.enqueue(
                common_checks_context,
                upload_dir,
                json_data,
                schema_obj,
                schema_name,
                context,
                job_id=job_id,
            )


def process_monitor_cove(project):
    job_id = project["name"] + "_cove_results"
    try:
        job = Job.fetch(job_id, connection=django_rq.get_connection())
        return {
            "status": job.get_status(),
            "result": job.result,
        }
    except NoSuchJobError:
        return {"status": "nosuchjob"}
