#!/usr/bin/env python3
import argparse
import asyncio
import os
from uuid import uuid4

import structlog

from ums.config import settings
from ums.models.identity import Identity
from ums.storage.sqlite import SQLiteStorage
from ums.utils.datetime import now_utc

logger = structlog.get_logger()


async def main():
    parser = argparse.ArgumentParser(description="Create a UMS user")
    parser.add_argument("--name", required=True, help="User display name")
    args = parser.parse_args()

    api_key = str(uuid4())
    db_path = settings.database_url.replace("sqlite+aiosqlite://", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    storage = SQLiteStorage(settings.database_url)
    await storage.initialize()

    identity = Identity(
        name=args.name,
        confidence=1.0,
    )
    await storage.create_identity(identity)
    await storage.close()

    print(f"User '{args.name}' created successfully.")
    print(f"Identity ID: {identity.id}")
    print(f"API Key: {api_key}")
    print()
    print("Set this API key as ADMIN_API_KEY in your .env file to authenticate.")


if __name__ == "__main__":
    asyncio.run(main())
