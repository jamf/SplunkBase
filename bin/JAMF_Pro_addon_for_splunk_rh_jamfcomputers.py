
import jamf_pro_addon_for_splunk_declare

from splunktaucclib.rest_handler.endpoint import (
    field,
    validator,
    RestModel,
    DataInputModel,
)
from splunktaucclib.rest_handler import admin_external, util
from splunk_aoblib.rest_migration import ConfigMigrationHandler

util.remove_http_proxy_env_vars()


fields = [
    field.RestField(
        'interval',
        required=True,
        encrypted=False,
        default=None,
        validator=validator.Pattern(
            regex=r"""^\-[1-9]\d*$|^\d*$""", 
        )
    ), 
    field.RestField(
        'index',
        required=True,
        encrypted=False,
        default='default',
        validator=validator.String(
            min_len=1, 
            max_len=80, 
        )
    ), 
    field.RestField(
        'name_of_the_modular_input',
        required=False,
        encrypted=False,
        default=None,
        validator=validator.String(
            min_len=0, 
            max_len=8192, 
        )
    ), 
    field.RestField(
        'jss_url',
        required=True,
        encrypted=False,
        default=None,
        validator=validator.String(
            min_len=0, 
            max_len=8192, 
        )
    ), 
    field.RestField(
        'jss_username',
        required=True,
        encrypted=False,
        default=None,
        validator=validator.String(
            min_len=0, 
            max_len=8192, 
        )
    ), 
    field.RestField(
        'jss_password',
        required=True,
        encrypted=True,
        default=None,
        validator=validator.String(
            min_len=0, 
            max_len=8192, 
        )
    ), 
    field.RestField(
        'excludeNoneManaged',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'sections',
        required=False,
        encrypted=False,
        default='PURCHASING~APPLICATIONS~HARDWARE~OPERATING_SYSTEM~EXTENSION_ATTRIBUTES~GROUP_MEMBERSHIPS~SECURITY',
        validator=None
    ), 
    field.RestField(
        'days_since_contact',
        required=False,
        encrypted=False,
        default='0',
        validator=validator.String(
            min_len=0, 
            max_len=8192, 
        )
    ), 
    field.RestField(
        'event_time_format',
        required=False,
        encrypted=False,
        default='timeAsScript',
        validator=None
    ), 
    field.RestField(
        'host_as_device_name',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'use_proxy',
        required=False,
        encrypted=False,
        default=None,
        validator=None
    ), 

    field.RestField(
        'disabled',
        required=False,
        validator=None
    )

]
model = RestModel(fields, name=None)



endpoint = DataInputModel(
    'jamfcomputers',
    model,
)


if __name__ == '__main__':
    admin_external.handle(
        endpoint,
        handler=ConfigMigrationHandler,
    )
