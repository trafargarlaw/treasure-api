import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus
from sqlmodel import and_, col, desc, select

from src.app.system.models import User
from src.app.system.schema.user import (
    AddSuperAdminParam,
    AddUserParam,
    AvatarParam,
    UpdateUserParam,
    UpdateUserRoleParam,
)
from src.common.security.jwt import get_hash_password
from src.utils.timezone import timezone


class CRUDUser(CRUDPlus[User]):
    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        """
        Get user

        :param db:
        :param user_id:
        :return:
        """
        return await self.select_model(db, user_id)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """
        Get user by username

        :param db:
        :param username:
        :return:
        """
        return await self.select_model_by_column(db, username=username)

    async def update_login_time(self, db: AsyncSession, username: str) -> int:
        """
        Update user login time

        :param db:
        :param username:
        :return:
        """
        return await self.update_model_by_column(db, {'last_login_time': timezone.now()}, username=username)

    async def add(self, db: AsyncSession, obj: AddUserParam | AddSuperAdminParam) -> None:
        """
        Add user from admin panel

        :param db:
        :param obj:
        :return:
        """
        salt = bcrypt.gensalt()
        obj.password = get_hash_password(f'{obj.password}', salt)
        dict_obj = obj.model_dump()
        dict_obj.update({'salt': salt})
        new_user = self.model(**dict_obj)
        db.add(new_user)

    async def update_userinfo(self, db: AsyncSession, input_user: int, obj: UpdateUserParam) -> int:
        """
        Update user information

        :param db:
        :param input_user:
        :param obj:
        :return:
        """
        return await self.update_model(db, input_user, obj)

    @staticmethod
    async def update_role(db: AsyncSession, input_user: User, obj: UpdateUserRoleParam) -> None:
        """
        Update user roles

        :param db:
        :param input_user:
        :param obj:
        :return:
        """
        # Remove all user roles

    async def update_avatar(self, db: AsyncSession, input_user: int, avatar: AvatarParam) -> int:
        """
        Update user avatar

        :param db:
        :param input_user:
        :param avatar:
        :return:
        """
        return await self.update_model(db, input_user, {'avatar': avatar.url})

    async def delete(self, db: AsyncSession, user_id: int) -> int:
        """
        Delete user

        :param db:
        :param user_id:
        :return:
        """
        return await self.delete_model(db, user_id)

    async def check_email(self, db: AsyncSession, email: str) -> User | None:
        """
        Check if email exists

        :param db:
        :param email:
        :return:
        """
        return await self.select_model_by_column(db, email=email)

    async def reset_password(self, db: AsyncSession, pk: int, new_pwd: str) -> int:
        """
        Reset user password

        :param db:
        :param pk:
        :param new_pwd:
        :return:
        """
        return await self.update_model(db, pk, {'password': new_pwd})

    async def get_list(
        self,
        username: str | None = None,
        status: int | None = None,
    ):
        """
        Get user list
        """
        stmt = select(self.model).order_by(desc(self.model.join_time))
        where_list = []
        if username:
            where_list.append(col(self.model.username).contains(username))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_super(self, db: AsyncSession, user_id: int) -> bool:
        """
        Get user superuser status

        :param db:
        :param user_id:
        :return:
        """
        user = await self.get(db, user_id)
        if user:
            return user.is_superuser
        return False

    async def get_status(self, db: AsyncSession, user_id: int) -> int:
        """
        Get user status

        :param db:
        :param user_id:
        :return:
        """
        user = await self.get(db, user_id)
        if user:
            return user.status
        return 0

    async def get_multi_login(self, db: AsyncSession, user_id: int) -> bool:
        """
        Get user multi-login status

        :param db:
        :param user_id:
        :return:
        """
        user = await self.get(db, user_id)
        if user:
            return user.is_multi_login
        return False

    async def set_super(self, db: AsyncSession, user_id: int, _super: bool) -> int:
        """
        Set user superuser status

        :param db:
        :param user_id:
        :param _super:
        :return:
        """
        return await self.update_model(db, user_id, {'is_superuser': _super})

    async def set_status(self, db: AsyncSession, user_id: int, status: bool) -> int:
        """
        Set user status

        :param db:
        :param user_id:
        :param status:
        :return:
        """
        return await self.update_model(db, user_id, {'status': status})

    async def set_multi_login(self, db: AsyncSession, user_id: int, multi_login: bool) -> int:
        """
        Set user multi-login status

        :param db:
        :param user_id:
        :param multi_login:
        :return:
        """
        return await self.update_model(db, user_id, {'is_multi_login': multi_login})

    async def get_with_relation(
        self,
        db: AsyncSession,
        *,
        user_id: int | None = None,
        username: str | None = None,
    ) -> User | None:
        """
        Get user with relations (department, roles, rules)
        """
        stmt = select(self.model)
        filters = []
        if user_id:
            filters.append(self.model.id == user_id)
        if username:
            filters.append(self.model.username == username)
        if filters:
            stmt = stmt.where(*filters)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return user


user_dao: CRUDUser = CRUDUser(User)
