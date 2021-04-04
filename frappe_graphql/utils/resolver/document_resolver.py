from graphql import GraphQLResolveInfo

import frappe
from frappe.model import default_fields

from .utils import get_singular_doctype


def document_resolver(obj, info: GraphQLResolveInfo, **kwargs):
    doctype = obj.get('doctype') or get_singular_doctype(info.parent_type.name)
    if not doctype:
        return None

    frappe.has_permission(doctype=doctype, doc=obj.get("name"), throw=True)

    # check if requested field can be resolved
    if isinstance(obj, dict):
        resolved_field_name = (obj or {}).get(info.field_name)
        if resolved_field_name:
            return resolved_field_name

    cached_doc = frappe.get_cached_doc(doctype, obj.get("name"))
    # verbose check of is_owner of doc
    role_permissions = frappe.permissions.get_role_permissions(doctype)
    if role_permissions.get("if_owner", {}).get("read"):
        if cached_doc.get("owner") != frappe.session.user:
            frappe.throw(frappe._("No permission for {0}").format(doctype + " " + obj.get("name")))
    # apply field level read perms
    cached_doc.apply_fieldlevel_read_permissions()
    meta = frappe.get_meta(doctype)

    df = meta.get_field(info.field_name)
    if not df:
        if info.field_name in default_fields:
            df = get_default_field_df(info.field_name)

    if info.field_name.endswith("__name"):
        fieldname = info.field_name.split("__name")[0]
        return cached_doc.get(fieldname)
    elif df and df.fieldtype == "Link":
        if not cached_doc.get(df.fieldname):
            return None
        return frappe._dict(name=cached_doc.get(df.fieldname), doctype=df.options)
    else:
        return cached_doc.get(info.field_name)


def get_default_field_df(fieldname):
    df = frappe._dict(
        fieldname=fieldname,
        fieldtype="Data"
    )
    if fieldname in ("owner", "modified_by"):
        df.fieldtype = "Link"
        df.options = "User"

    return df
