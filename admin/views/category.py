from starlette_admin.contrib.sqla import ModelView


class CategoryAdmin(ModelView):
    label = "Категории"
