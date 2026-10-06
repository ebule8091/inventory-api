import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(database_url, pool_pre_ping=True)


if __name__ == "__main__":
    with engine.connect() as connection:
        info = connection.execute(
            text("SELECT DATABASE(), @@hostname, @@port")
        ).one()

        print("Database:", info[0])
        print("Server:", info[1])
        print("Port:", info[2])

        count = connection.execute(
            text("SELECT COUNT(*) FROM products")
        ).scalar_one()

        print("Saved products:", count)


from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
)


def get_db():
    with SessionLocal() as session:
        yield session