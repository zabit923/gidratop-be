from starlette_admin.contrib.sqla import ModelView


class CardAdmin(ModelView):
    label = "Карточки"
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
