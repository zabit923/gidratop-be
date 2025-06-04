from starlette_admin.contrib.sqla import ModelView


class PaymentMethodAdmin(ModelView):
    label = "Способы оплаты"
