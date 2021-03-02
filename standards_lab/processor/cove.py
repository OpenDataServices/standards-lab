from libcove.lib.common import (
    common_checks_context,
    SchemaJsonMixin,
    validator,
)

from decimal import Decimal
from urllib.parse import urljoin
import json
import os
import tempfile

import django_rq
from rq.job import Job
from rq.exceptions import NoSuchJobError

from .extra_validator_funcs import patch_validator


patch_validator(validator)


def start(project):
    schema_name = project["rootSchema"]

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

    output = {}
    for data_file in project["dataFiles"]:
        context = {"file_type": "json"}

        job_id = project["name"] + "_cove_results_" + data_file
        try:
            job = Job.fetch(job_id, connection=django_rq.get_connection())
            status = job.get_status()
            if status not in ["finished", "failed"]:
                output[data_file] = {
                    "status": "FAILED",
                    "error": f"Job exists, and status is '{status}', so not"
                    " queuing a new job.",
                }
                continue
        except NoSuchJobError:
            pass

        with open(
            os.path.join(project["path"], data_file)
        ) as fp, tempfile.TemporaryDirectory() as upload_dir:
            # upload_dir is only used to output files to (e.g. cell source map
            # from flatten-tool, or a cache of the validation results).
            try:
                # Possibly we should do this in the worker for performance reasons
                # Issue: https://github.com/OpenDataServices/standards-lab/issues/24
                json_data = json.load(fp, parse_float=Decimal)
            except json.JSONDecodeError:
                output[data_file] = {
                    "status": "FAILED",
                    "error": "Could not decode as a json file",
                }
                continue

            job = django_rq.enqueue(
                common_checks_context,
                upload_dir,
                json_data,
                schema_obj,
                schema_name,
                context,
                cache=False,
                job_id=job_id,
            )
            output[data_file] = {"status": "SUCCESS"}
    return output


def monitor(project):
    """

    ```
    {
        "cove": {
            "1-data_file_name.json": {
                # status message from Redis, or "nosuchjob" if the job doesn't exist at all
                # https://python-rq.org/docs/jobs/#retrieving-a-job-from-redis
                # Possible values are "queued", "started", "deferred",
                # "finished", "stopped", "failed" and "nosuchjob".
                # Different to "status" returned by other calls, which is the
                # status of the django api call.
                "rq_status": "finished",
                # lib-cove's `context` output
                "result" : {...}
            }
        }
    }
    ```

    """

    output = {}
    for data_file in project["dataFiles"]:
        job_id = project["name"] + "_cove_results_" + data_file
        try:
            job = Job.fetch(job_id, connection=django_rq.get_connection())
            output[data_file] = {
                "rq_status": job.get_status(),
                "result": job.result,
            }
        except NoSuchJobError:
            output[data_file] = {"rq_status": "nosuchjob"}
    return output
