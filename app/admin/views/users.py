from starlette_admin.contrib.sqla import ModelView


class UserAdmin(ModelView):
    label = "Пользователи"
    exclude_fields_from_list = [
        "phone",
        "hashed_password",
        "first_name",
        "last_name",
        "middle_name",
        "birth_date",
        "gender",
        "avatar",
        "is_active",
        "balance",
        "bonus_points",
        "cashback_balance",
        "email_notifications",
        "sms_notifications",
        "push_notifications",
        "marketing_consent",
        "referral_code",
        "total_orders",
        "total_spent",
        "last_order_date",
        "last_login",
        "registration_source",
        "referred_by",
        "addresses",
        "payment_methods",
        "cart",
    ]
    searchable_fields = [
        "username",
        "email",
        "phone",
        "first_name",
        "last_name",
        "middle_name",
    ]
    exclude_fields_from_detail = [
        "cart",
        "payment_methods",
        "addresses",
    ]
