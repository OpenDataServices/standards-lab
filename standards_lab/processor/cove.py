from libcove.lib.common import (
    common_checks_context,
    SchemaJsonMixin,
    validator,
)
from libcove.lib.converters import convert_spreadsheet
from libcove.config import LibCoveConfig

from decimal import Decimal
from urllib.parse import urljoin
import json
import os
import tempfile

import django_rq
import jsonref
from rq.job import Job
from rq.exceptions import NoSuchJobError

import api.views
from .extra_validator_funcs import patch_validator


patch_validator(validator)


MIME_TYPE_TO_FILE_TYPE = {
    "application/csv": "csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.oasis.opendocument.spreadsheet": "ods",
}


def lib_cove_wrapper(
    project,
    data_file,
    cache=False,
):
    """
    A wrapper around common_checks_context and convert_spreadsheet from
    lib-cove.

    This is the function that gets queued at the moment.  This means that
    conversion happens automatically, but also means you can't run the
    conversion on its own beforehand.

    """

    schema_name = project["rootSchema"]
    root_list_path = project.get("rootListPath", "")

    schema_obj = SchemaJsonMixin()

    schema_obj.schema_host = os.path.join(project["path"], "")
    # Don't set schema_obj.schema_name or schema_obj.schema_url, because these
    # are only used by flatten-tool, which requires a specific subschema, see
    # comment above flattentool_schema_url below.
    schema_obj.pkg_schema_name = schema_name
    schema_obj.pkg_schema_url = urljoin(
        schema_obj.schema_host, schema_obj.pkg_schema_name
    )

    data_file_path = os.path.join(project["path"], data_file)
    mime_type = api.views.check_allowed_project_mime_type(data_file_path)
    file_type = MIME_TYPE_TO_FILE_TYPE.get(mime_type, "json")
    context = {"file_type": file_type}

    # Only used for constructing the converted url, which currently wouldn't
    # work in standards-lab anyway, as the converted file isn't placed anywhere
    # web accessiable
    upload_url = "http://example.org/"

    lib_cove_config = LibCoveConfig()
    lib_cove_config.config["root_list_path"] = root_list_path
    # This is the name of an extra id at the top level, e.g. ocds has ocid. An
    # empty string means no such id
    lib_cove_config.config["root_id"] = ""

    # upload_dir is only used to output files to (e.g. cell source map from
    # flatten-tool, or a cache of the validation results), so we don't have to
    # set it to where the standards-lab data was uploaded
    with tempfile.TemporaryDirectory() as upload_dir:
        # flatten-tool takes a schema url or path, but it expects the
        # sub-schema describing the repeated object, not the package schema.
        # e.g. the schema describing a grant in 360Giving or a release in OCDS.
        #
        # For the existing standards we work on, this is a seperate file which
        # we can point flatten-tool at. But, in standards-lab we don't know
        # which schema file it is, or whether the schema files are even split
        # this way. Instead, we deref to combine all the schemas, and find the
        # sub-schema we want from the package schema, write that out to a file,
        # and pass it to flatten-tool.
        flattentool_schema_url = os.path.join(upload_dir, "flattentool_schema.json")

        with open(schema_obj.pkg_schema_url) as schema_fp, open(
            flattentool_schema_url, "w"
        ) as flattentool_schema_fp:
            schema = jsonref.load(schema_fp)
            flattentool_schema = (
                schema.get("properties", {}).get(root_list_path, {}).get("items", {})
            )
            json.dump(flattentool_schema, flattentool_schema_fp)

        if file_type != "json":
            context.update(
                convert_spreadsheet(
                    upload_dir,
                    upload_url,
                    data_file_path,
                    file_type,
                    lib_cove_config,
                    schema_url=flattentool_schema_url,
                    pkg_schema_url=schema_obj.pkg_schema_url,
                    metatab_name="Meta",
                    replace=True,
                    cache=False,
                )
            )

            json_file_path = context["converted_path"]

        else:
            json_file_path = data_file_path

        with open(json_file_path) as fp:
            try:
                json_data = json.load(fp, parse_float=Decimal)
            except json.JSONDecodeError:
                context.update(
                    {
                        "status": "FAILED",
                        "error": "Could not decode as a json file",
                    }
                )
                return context

            context = common_checks_context(
                upload_dir,
                json_data,
                schema_obj,
                schema_name,
                context,
                cache=False,
            )
    context["status"] = "SUCCESS"
    return context


def start(project):
    output = {}
    for data_file in project["dataFiles"]:
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

        job = django_rq.enqueue(
            lib_cove_wrapper,
            project,
            data_file,
            job_id=job_id,
            result_ttl=2 * 60 * 60,
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
    project_data_files = project.get("dataFiles")

    if project_data_files:
        for data_file in project_data_files:
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
