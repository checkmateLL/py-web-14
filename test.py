# import smtplib

# try:
#     server = smtplib.SMTP_SSL("smtp.meta.ua", 465)
#     server.login("gotestuser@meta.ua", "C3rberus")
#     print("SMTP login successful")
# except smtplib.SMTPException as e:
#     print(f"SMTP error occurred: {e}")
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     server.quit()

from asyncpg import connect
from src.conf.config import settings

async def test_connection():
    conn = await connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=settings.postgres_port
    )
    print("Database connected!")
    await conn.close()
