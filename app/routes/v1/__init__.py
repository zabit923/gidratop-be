from app.routes.base import BaseRouter
from app.routes.v1.auth import AuthRouter
from app.routes.v1.categories import CategoryRouter
from app.routes.v1.registration import RegisterRouter
from app.routes.v1.verification import VerificationRouter


class APIv1(BaseRouter):
    def configure_routes(self):
        self.router.include_router(RegisterRouter().get_router())
        self.router.include_router(AuthRouter().get_router())
        self.router.include_router(VerificationRouter().get_router())
        self.router.include_router(CategoryRouter().get_router())
        # self.router.include_router(OAuthRouter().get_router())
        # self.router.include_router(UserRouter().get_router())
        # self.router.include_router(ProfileRouter().get_router())
