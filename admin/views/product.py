from starlette_admin.contrib.sqla import ModelView


class ProductAdmin(ModelView):
    label = "Продукты"
