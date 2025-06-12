from starlette_admin.contrib.sqla import ModelView


class CartItemAdmin(ModelView):
    label = "Товары в корзине"
