from app.routes.base import BaseRouter


class ProductRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="cards", tags=["Cards"])
