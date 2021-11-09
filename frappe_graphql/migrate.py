import frappe
from frappe.utils import cint
from frappe_graphql.utils.cache import GraphqlSchemaCache
from frappe_graphql.utils.loader import build_graphql_schema


def after_migrate():
    handle_graphql_schema_cache()


def handle_graphql_schema_cache():
    """
    Lets clear and set the schema in redis only if developer mode == False
    """
    if not cint(frappe.local.conf.developer_mode):
        cache = GraphqlSchemaCache()
        cache.delete_schema_from_cache()
        schema = build_graphql_schema()
        frappe.log_error(schema.to_kwargs())
        cache.set_schema_in_cache(schema)
