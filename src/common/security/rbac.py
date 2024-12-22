import casbin
import casbin_async_sqlalchemy_adapter

from fastapi import Depends, Request

from src.app.system.models import CasbinRule
from src.common.exception.errors import AuthorizationError, TokenError
from src.common.security.jwt import DependsJwtAuth
from src.core.conf import settings
from src.database.db_postgres import async_engine


class RBAC:
    @staticmethod
    async def enforcer() -> casbin.AsyncEnforcer:
        """
        Get casbin enforcer

        :return:
        """
        # Model definition: https://casbin.org/zh/docs/category/model
        _CASBIN_RBAC_MODEL_CONF_TEXT = """
        [request_definition]
        r = sub, obj, act

        [policy_definition]
        p = sub, obj, act

        [role_definition]
        g = _, _

        [policy_effect]
        e = some(where (p.eft == allow))

        [matchers]
        m = g(r.sub, p.sub) && (keyMatch(r.obj, p.obj) || keyMatch3(r.obj, p.obj)) && (r.act == p.act || p.act == "*")
        """
        adapter = casbin_async_sqlalchemy_adapter.Adapter(
            async_engine, db_class=CasbinRule
        )
        model = casbin.AsyncEnforcer.new_model(text=_CASBIN_RBAC_MODEL_CONF_TEXT)
        enforcer = casbin.AsyncEnforcer(model, adapter)
        await enforcer.load_policy()
        return enforcer

    async def rbac_verify(self, request: Request, _token: str = DependsJwtAuth) -> None:
        """
        RBAC permission verification (authorization order is important, modify with caution)

        :param request:
        :param _token:
        :return:
        """
        path = request.url.path

        # API authorization whitelist
        if path in settings.TOKEN_REQUEST_PATH_EXCLUDE:
            return

        # Force JWT authorization status check
        if not request.auth.scopes:
            raise TokenError

        # Super admin bypass verification
        if request.user.is_superuser:
            return

        # Check backend management operation permissions
        method = request.method
        # if method != "GET" and method != "OPTIONS":
        #     raise AuthorizationError(
        #         msg="User is forbidden from backend management operations, please contact system administrator"
        #     )

        # Casbin authorization whitelist
        if (method, path) in settings.RBAC_CASBIN_EXCLUDE:
            return

        # Casbin permission verification
        # Implementation mechanism: backend/app/admin/api/v1/sys/casbin.py
        user_uuid = request.user.uuid
        enforcer = await self.enforcer()
        result = enforcer.enforce(user_uuid, path, method)

        if not result:
            raise AuthorizationError


rbac: RBAC = RBAC()
# RBAC authorization dependency injection
DependsRBAC = Depends(rbac.rbac_verify)
