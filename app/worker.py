import os
import time
from app.db import SessionLocal
from app.repositories import FileRepository


def main() -> None:
    interval = int(os.getenv('FILES_CLEANUP_INTERVAL_SECONDS', '30'))
    while True:
        with SessionLocal() as session:
            FileRepository(session).cleanup_leases()
        time.sleep(interval)


if __name__ == '__main__':
    main()
