from sqlalchemy import text

from app.db.database import SessionLocal

try: 
    with SessionLocal() as session:
        result = session.execute(text("SELECT 1"))
        print(result.scalar())


        print("Conexión correcta a la base de datos.")

except Exception as e:
    print("Error al conectar a la base de datos:")
    print(e)
