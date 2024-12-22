import asyncio

import click

from fastapi import Request as FastAPIRequest
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.datastructures import Headers

from src.app.system.models.hints import Hint
from src.app.system.service.user_service import user_service
from src.common.loader import load_hints, load_super_admin
from src.database.db_postgres import async_engine


class MockRequest(FastAPIRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = None

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value


@click.command()
@click.option('--hints', is_flag=True, help='Seed hints')
def seed(hints: bool):
    """Seed the database with initial data"""
    if hints:
        asyncio.run(seed_hints())
    else:
        asyncio.run(seed_super_admin())


async def seed_super_admin():
    try:
        admin_data = load_super_admin()
        mock_request = MockRequest({'type': 'http', 'headers': Headers()})
        mock_request.user = type('User', (), {'is_superuser': True})()

        await user_service.add(request=mock_request, obj=admin_data)
        click.echo('Super admin seeded successfully!')
    except Exception as e:
        click.echo(f'Error seeding super admin: {str(e)}', err=True)


async def seed_hints():
    try:
        hints = load_hints()

        async with AsyncSession(async_engine) as db:
            id_counter = 1

            for coord, pois in hints.items():
                # Parse x,y from coordinate string
                x, y = map(int, coord.split(','))

                # For each POI at this coordinate
                for poi in pois:
                    id = id_counter
                    names = poi['name']
                    hint = Hint(
                        id=id,
                        posX=x,
                        posY=y,
                        hint_en=names.get('en', ''),
                        hint_fr=names.get('fr', ''),
                        hint_es=names.get('es', ''),
                        hint_de=names.get('de', ''),
                        hint_pt=names.get('pt', ''),
                    )
                    db.add(hint)
                    id_counter += 1
            await db.commit()
    except Exception as e:
        click.echo(f'Error seeding case types: {str(e)}', err=True)
