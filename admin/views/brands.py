from starlette_admin.contrib.sqla import ModelView


class BrandAdmin(ModelView):
    label = "Бренды"
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
