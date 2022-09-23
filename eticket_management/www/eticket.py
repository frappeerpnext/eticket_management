

from multiprocessing import context
import frappe

no_cache = 1


def get_context(context):

    item = frappe.get_doc("Item","88888")
    item.description = "Mydev is good"
    item.save()
    frappe.db.commit()

    context.name = "hello"
    context.item =item
    