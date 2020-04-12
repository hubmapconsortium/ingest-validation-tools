class DirectoryValidationErrors(Exception):
    def __init__(self, errors):
        self.json_validation_errors = errors
        self.object_errors = [
            _validation_error_to_object(e)
            for e in errors
        ]

    def __str__(self):
        return '\n'.join(self.object_errors)

    def __repr__(self):
        return self.json_validation_error.__repr__()


def _validation_error_to_object(error):
    instance_type = type(error.instance)

    if instance_type == str:
        instance_description = 'This string'
        instance_details = error.instance
    elif instance_type == list:
        instance_description = 'This directory'
        instance_details = _to_names([error.instance])
    elif instance_type == dict:
        instance_description = f'This {error.instance["type"]}'
        instance_details = error.instance['name']
    else:
        instance_description = 'This item'
        instance_details = _to_names(error.instance)

    if error.validator == 'pattern':
        validator_description = "doesn't match this pattern"
    elif error.validator == 'enum':
        validator_description = "is not one of the expected enum values"
    elif error.validator == 'oneOf':
        validator_description = "doesn't match exactly one of these"
    elif error.validator == 'allOf':
        validator_description = "doesn't match all of these"
    elif error.validator == 'contains':
        validator_description = "should contain"
    else:
        validator_description = f'fails this "{error.validator}" check'
    validator_details = error.schema[error.validator]
    return {
        instance_description: instance_details,
        validator_description: validator_details
    }


def _to_names(dir_as_list):
    return {
        item['name']: (item['contents'] if 'contents' in item else [])
        for item in dir_as_list
    }
