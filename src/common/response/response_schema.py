from datetime import datetime
from typing import Generic, TypeVar

from fastapi import Response
from pydantic import BaseModel, ConfigDict

from src.common.response.response_code import CustomResponse, CustomResponseCode
from src.core.conf import settings

# _ExcludeData = IncEx

__all__ = ["ResponseModel", "response_base"]

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """
    Unified Response Model with generic type support for data field
    """

    model_config = ConfigDict(
        json_encoders={datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)}
    )

    code: int = CustomResponseCode.HTTP_200.code
    msg: str = CustomResponseCode.HTTP_200.msg
    data: T | None = None


class ResponseBase:
    """
    Unified Response Methods

    .. tip::

        Methods in this class will return a ResponseModel model, existing as a coding style;

    E.g. ::

        @router.get('/test')
        def test() -> ResponseModel:
            return response_base.success(data={'test': 'test'})
    """

    @staticmethod
    def __response(
        *,
        res: CustomResponseCode | CustomResponse,
        data: T | None = None,
    ) -> ResponseModel[T]:
        """
        Common method for successful request responses

        :param res: Response information
        :param data: Response data
        :return:
        """
        return ResponseModel[T](code=res.code, msg=res.msg, data=data)

    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: T | None = None,
    ) -> ResponseModel[T]:
        return self.__response(res=res, data=data)

    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: T = None,
    ) -> ResponseModel[T]:
        return self.__response(res=res, data=data)

    @staticmethod
    def fast_success(
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: object | None = None,
    ) -> Response:
        """
        This method is created to improve API response speed. If the return data doesn't need pydantic parsing and validation,
        it's recommended to use this method. Otherwise, please don't use it!

        .. warning::

            When using this return method, don't specify the response_model parameter in the API,
            and don't add arrow return type after the API function

        :param res:
        :param data:
        :return:
        """

        return Response(
            status_code=res.code,
            content={"code": res.code, "msg": res.msg, "data": data},
        )


response_base: ResponseBase = ResponseBase()
