import json

import frappe
from graphql import GraphQLSchema

FRAPPE_GRAPHQL_SCHEMA_REDIS_KEY = "graphql_schema"


class GraphqlSchemaCache(object):
    def __init__(self):
        self.redis_server = frappe.cache()
        self.current_site = frappe.local.site
        self.redis_key = f"{FRAPPE_GRAPHQL_SCHEMA_REDIS_KEY}_{self.current_site}"

    def get_schema_from_redis(self):
        return self.redis_server.get_value(self.redis_key)

    def set_schema_in_cache(self, schema: GraphQLSchema):
        self.redis_server.set_value(self.redis_key, json.dumps(schema.to_kwargs()))
        return self.get_schema_from_redis()

    def delete_schema_from_cache(self):
        self.redis_server.delete_key(self.redis_key)
