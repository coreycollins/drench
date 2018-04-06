"""taxonomy!"""

TYPE_INDEX = {
    "string": str,
    "integer": int,
    "boolean": bool
}

class Taxonomy(object):
    """file layout"""
    def __init__(self, format_type, fields):
        self.format_type = format_type
        self.fields = fields

        for field in fields:
            f_t = field['field_type']
            if f_t not in TYPE_INDEX.keys():
                raise BaseException(f'undefined field type {f_t}')
