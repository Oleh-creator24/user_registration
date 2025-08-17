from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ValidationError


# ----- Модель Address -----
class Address(BaseModel):
    city: str = Field(..., min_length=2, description="Название города (мин. 2 символа)")
    street: str = Field(..., min_length=3, description="Название улицы (мин. 3 символа)")
    house_number: int = Field(..., gt=0, description="Номер дома (положительное число)")


# ----- Модель User -----
class User(BaseModel):
    name: str = Field(..., min_length=2, description="Имя должно состоять из букв")
    age: int = Field(..., ge=0, le=120, description="Возраст 0–120")
    email: EmailStr
    is_employed: bool
    address: Address

    # Имя: только буквы и пробелы
    @field_validator("name")
    @classmethod
    def name_must_be_letters(cls, v: str) -> str:
        # Разрешаем пробелы между словами; удаляем пробелы и проверяем, что остались только буквы (Unicode)
        if not v.replace(" ", "").isalpha():
            raise ValueError("Имя должно содержать только буквы (пробелы допустимы)")
        return v

    # Проверка возраста и занятости: выполняется после валидации всех полей
    @model_validator(mode="after")
    def check_age_vs_employment(self):
        if self.is_employed and not (18 <= self.age <= 65):
            raise ValueError("Если пользователь работает, возраст должен быть от 18 до 65 лет")
        return self


# ----- Функция обработки JSON -----
def process_user_registration(json_str: str) -> str:
    """
    Принимает JSON-строку, валидирует в модели Pydantic, и
    при успехе возвращает сериализованный JSON (красиво отформатированный).
    В случае ошибок — текст ошибки валидации.
    """
    try:
        user = User.model_validate_json(json_str)          # десериализация + валидация
        return user.model_dump_json(indent=4)              # сериализация обратно в JSON
    except ValidationError as e:
        return f"Ошибка валидации:\n{e}"


# ----- Тестовые случаи -----
if __name__ == "__main__":
    test_cases = [
        # ✅ Успешная регистрация (работает)
        """
        {
            "name": "Alice Smith",
            "age": 30,
            "email": "alice.smith@example.com",
            "is_employed": true,
            "address": {
                "city": "Berlin",
                "street": "Hauptstrasse",
                "house_number": 10
            }
        }
        """,

        # ✅ Успешная регистрация (безработный подросток)
        """
        {
            "name": "Ivan Petrov",
            "age": 16,
            "email": "ivan.petrov@example.com",
            "is_employed": false,
            "address": {
                "city": "Madrid",
                "street": "Gran Via",
                "house_number": 22
            }
        }
        """,

        # ❌ Ошибка: возраст не подходит для работающего пользователя
        """
        {
            "name": "John Doe",
            "age": 70,
            "email": "john.doe@example.com",
            "is_employed": true,
            "address": {
                "city": "New York",
                "street": "5th Avenue",
                "house_number": 123
            }
        }
        """,

        # ❌ Ошибка: имя содержит цифру
        """
        {
            "name": "Bob1",
            "age": 40,
            "email": "bob@example.com",
            "is_employed": false,
            "address": {
                "city": "Paris",
                "street": "Rue de Rivoli",
                "house_number": 15
            }
        }
        """,

        # ❌ Ошибка: улица слишком короткая (мин. 3)
        """
        {
            "name": "Maria Lopez",
            "age": 28,
            "email": "maria.lopez@example.com",
            "is_employed": false,
            "address": {
                "city": "Rome",
                "street": "St",
                "house_number": 5
            }
        }
        """,

        # ❌ Ошибка: неверный email
        """
        {
            "name": "Olga Sidorova",
            "age": 35,
            "email": "olga_at_mail.com",
            "is_employed": false,
            "address": {
                "city": "Warsaw",
                "street": "Marszalkowska",
                "house_number": 8
            }
        }
        """
    ]

    for i, case in enumerate(test_cases, start=1):
        print(f"\n--- Тест {i} ---")
        print(process_user_registration(case))
