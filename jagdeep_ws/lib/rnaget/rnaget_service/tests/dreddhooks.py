import json
import dredd_hooks as hooks

UUID_EXAMPLE = "be2ba51c-8dfe-4619-b832-31c4a087a589"
VERSION = "0.9.3b"
RO_FIELDS = ["created", "id"]
response_stash = {}


@hooks.before_each
def redact_readonly_fields(transaction):
    """Do not POST readonly (computed) fields"""
    if transaction['request']['method'] == "POST":
        # otherwise, remove such fields from the request body
        request_body = json.loads(transaction['request']['body'])
        for ro_field in RO_FIELDS:
            if ro_field in request_body:
                del request_body[ro_field]
        transaction['request']['body'] = json.dumps(request_body)


@hooks.before("expressions > /rnaget/expressions > Create an expression database entry and map to quant file > 201 > application/json")
def set_expression_filetype(transaction):
    request_body = json.loads(transaction['request']['body'])
    request_body['fileType'] = "h5"
    request_body['__filepath__'] = 'dredd.yml'
    transaction['request']['body'] = json.dumps(request_body)


@hooks.before("changelog > /rnaget/changelog > Add a change log to the database > 201 > application/json")
def set_changelog_version(transaction):
    request_body = json.loads(transaction['request']['body'])
    request_body['version'] = VERSION
    transaction['request']['body'] = json.dumps(request_body)


@hooks.after("projects > /rnaget/projects/search > Search for projects matching filters > 200 > application/json")
def save_projects_response(transaction):
    parsed_body = json.loads(transaction['real']['body'])
    ids = [item['id'] for item in parsed_body]
    response_stash['project_ids'] = ids


@hooks.after("studies > /rnaget/studies/search > Search for studies matching filters > 200 > application/json")
def save_studies_response(transaction):
    parsed_body = json.loads(transaction['real']['body'])
    ids = [item['id'] for item in parsed_body]
    response_stash['study_ids'] = ids


@hooks.after("expressions > /rnaget/expressions > Search for all expressions > 200 > application/json")
def save_expressions_response(transaction):
    parsed_body = json.loads(transaction['real']['body'])
    ids = [item['id'] for item in parsed_body]
    response_stash['expression_ids'] = ids


@hooks.after("changelog > /rnaget/getVersions > Get release versions of database > 200 > application/json")
def save_versions_response(transaction):
    parsed_body = json.loads(transaction['real']['body'])
    versions = [item for item in parsed_body]
    response_stash['versions'] = versions


@hooks.before("projects > /rnaget/projects/{projectId} > Find project by ID > 200 > application/json")
def insert_project_id(transaction):
    transaction['fullPath'] = transaction['fullPath'].replace(UUID_EXAMPLE, response_stash['project_ids'][0])


@hooks.before("studies > /rnaget/studies/{studyId} > Find study by ID > 200 > application/json")
def insert_study_id(transaction):
    if 'project_ids' in response_stash:
        transaction['fullPath'] = transaction['fullPath'].replace(UUID_EXAMPLE, response_stash['study_ids'][0])


@hooks.before("expressions > /rnaget/expressions/{expressionId} > Find expression data by ID > 200 > application/json")
def insert_expression_id(transaction):
    if 'expression_ids' in response_stash:
        transaction['fullPath'] = transaction['fullPath'].replace(UUID_EXAMPLE, response_stash['expression_ids'][0])


@hooks.before("files > /rnaget/files/{fileID} > Get specific file > 200 > application/json")
def insert_file_id(transaction):
    transaction['fullPath'] = transaction['fullPath'].replace(UUID_EXAMPLE, response_stash['expression_ids'][0])


@hooks.before("changelog > /rnaget/changelog/{version} > Get change log for a specific release version > 200 > application/json")
def insert_change_version(transaction):
    if 'versions' in response_stash:
        transaction['fullPath'] = transaction['fullPath'].replace("version1", response_stash['versions'][0])


@hooks.before("projects > /rnaget/projects/{projectId} > Find project by ID > 404 > application/json")
@hooks.before("studies > /rnaget/studies/{studyId} > Find study by ID > 404 > application/json")
@hooks.before("expressions > /rnaget/expressions/{expressionId} > Find expression by ID > 404 > application/json")
def let_pass(transaction):
    transaction['skip'] = False
