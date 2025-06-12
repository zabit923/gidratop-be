from starlette_admin.contrib.sqla import ModelView


class CartAdmin(ModelView):
    label = "Корзины"
