from database import db_utils, models


def initialize_database():
    with models.SessionLocal() as session:
        user = session.query(models.User).filter_by(telegram_id=123456).first()
        if not user:
            user = models.User(telegram_id=123456, name="Тестовый Пользователь", phone="+1234567890",
                               email="test@example.com", role="client")
            session.add(user)

        db_utils.add_master_code(code="MASTER2024", description="Код для новых мастеров", user_id=None)

        services = [
            ("Стрижка", "Обычная стрижка", 500, 30),
            ("Окрашивание", "Полное окрашивание волос", 2000, 90),
            ("Маникюр", "Комплексный маникюр", 1000, 60),
        ]
        for name, description, price, duration in services:
            existing_service = session.query(models.Service).filter_by(name=name).first()
            if not existing_service:
                service = models.Service(name=name, description=description, price=price, duration_minutes=duration)
                session.add(service)

        session.commit()
        print("Данные успешно добавлены.")


if __name__ == "__main__":
    initialize_database()
