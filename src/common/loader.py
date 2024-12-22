import json

from typing import Dict, List, TypedDict

from src.app.system.schema.user import AddSuperAdminParam
from src.core.conf import settings


class PoiName(TypedDict):
    id: str
    en: str
    es: str
    pt: str
    de: str
    fr: str


class PointOfInterest(TypedDict):
    _id: str
    id: int
    categoryId: int
    className: str
    name: PoiName
    m_id: int
    createdAt: str
    updatedAt: str


def load_super_admin() -> AddSuperAdminParam:
    """Load super admin credentials from environment variables"""
    return AddSuperAdminParam(
        username=settings.SUPER_ADMIN_USERNAME,
        email=settings.SUPER_ADMIN_EMAIL,
        password=settings.SUPER_ADMIN_PASSWORD,
        status=1,
        is_superuser=True,
        is_multi_login=True,
    )


def load_hints() -> Dict[str, List[PointOfInterest]]:
    try:
        hints = json.load(open('src/fixtures/treasure_hunt_pois.json'))
    except FileNotFoundError:
        raise Exception('Hints file not found')
    except Exception as e:
        raise Exception(f'Failed to load hints: {str(e)}')

    return hints
