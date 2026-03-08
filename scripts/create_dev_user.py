import asyncio
from uuid import UUID

from sqlalchemy import select

from src.infrastructure.config.settings import get_settings
from src.infrastructure.persistence.database import get_engine
from src.infrastructure.persistence.models.user_model import UserDB


async def create_dev_user():
    print("Vérification de l'utilisateur dev...")
    engine = get_engine()

    # We use a session to check and add
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        user_id = UUID("00000000-0000-0000-0000-000000000000")
        result = await session.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            print(f"Création de l'utilisateur dev {user_id}...")
            new_user = UserDB(
                id=user_id,
                email="dev@mptoo.dev",
                password_hash="fake",
                name="Dev User",
                role="admin",
                is_active=True,
            )
            session.add(new_user)
            await session.commit()
            print("Utilisateur dev créé.")
        else:
            print("L'utilisateur dev existe déjà.")


if __name__ == "__main__":
    asyncio.run(create_dev_user())
