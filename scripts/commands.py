import os
import subprocess
from pathlib import Path
from typing import Optional
import time
import socket
import platform
import uvicorn


class DockerDaemonNotRunningError(Exception):
    """
    Исключение, возникающее когда Docker демон не запущен или недоступен.
    """
    def __init__(self, message=None):
        self.message = message or "Docker демон не запущен. Убедись, что Docker Desktop запущен и работает."
        super().__init__(self.message)


class DockerContainerConflictError(Exception):
    """
    Исключение, возникающее при конфликте имен контейнеров Docker.
    """
    def __init__(self, container_name=None, message=None):
        if container_name:
            self.message = message or f"Конфликт имен контейнеров. Контейнер '{container_name}' уже используется. Удали его или переименуй."
        else:
            self.message = message or "Конфликт имен контейнеров. Удали существующий контейнер или переименуй его."
        super().__init__(self.message)

ENV_FILE=".env.dev"
# Получаем путь к корню проекта
ROOT_DIR = Path(__file__).parents[1]

COMPOSE_FILE_WITHOUT_BACKEND = "docker-compose.dev.yml"

DEFAULT_PORTS = {
    'FASTAPI': 8000,
    'RABBITMQ': 5672,      # Порт для AMQP
    'RABBITMQ_UI': 15672,  # Порт для веб-интерфейса
    'POSTGRES': 5432,
    'REDIS': 6379,
    'PGADMIN': 5050,
    'REDIS_COMMANDER': 8081,
}
def load_env_vars(env_file_path: str = None) -> dict:
    """
    Загружает переменные окружения из .env файла

    Args:
        env_file_path: Путь к файлу .env. Если None, используется ENV_FILE из констант

    Returns:
        dict: Словарь с переменными окружения
    """
    if env_file_path is None:
        env_file_path = os.path.join(ROOT_DIR, ENV_FILE)

    env_vars = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
                    except ValueError:
                        # Пропускаем некорректные строки
                        pass
    return env_vars

def run_compose_command(command: str | list, compose_file: str = COMPOSE_FILE_WITHOUT_BACKEND, env: dict = None) -> None:
    """
    Запускает docker-compose команду в корне проекта

    Args:
        command: Команда для docker-compose
        compose_file: Путь к docker-compose файлу. По умолчанию используется COMPOSE_FILE_WITHOUT_BACKEND из констант
        env: Переменные окружения для docker-compose. По умолчанию используется ENV_FILE из констант

    Returns:
        None

    Raises:
        DockerDaemonNotRunningError: Если демон Docker не запущен
        DockerContainerConflictError: Если контейнер уже запущен
        FileNotFoundError: Если файл .env.dev или docker-compose файл не найден
    """
    if isinstance(command, str):
        command = command.split()

    # Проверяем наличие файла docker-compose
    compose_path = os.path.join(ROOT_DIR, compose_file)
    if not os.path.exists(compose_path):
        print(f"❌ Файл {compose_file} не найден в директории {ROOT_DIR}")
        raise FileNotFoundError(f"❌ Файл {compose_file} не найден в {ROOT_DIR}")

    # Проверяем наличие .env.dev
    env_path = os.path.join(ROOT_DIR, ENV_FILE)
    if not os.path.exists(env_path):
        print(f"❌ Файл {ENV_FILE} не найден в директории {ROOT_DIR}")
        print("💡 Создайте файл .env.dev с необходимыми переменными окружения")
        raise FileNotFoundError(f"❌ Файл {ENV_FILE} не найден. Создайте его перед запуском.")

    # Обновляем переменные окружения
    environment = os.environ.copy()
    # Добавляем переменные из ENV_FILE
    environment.update(load_env_vars())
    if env:
        environment.update(env)

    try:
        subprocess.run(
            ["docker-compose", "-f", compose_file] + command,
            cwd=ROOT_DIR,
            check=True,
            env=environment,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or str(e)
        if "docker daemon is not running" in error_output or "pipe/docker_engine" in error_output:
            raise DockerDaemonNotRunningError() from e
        elif "Conflict" in error_output and "is already in use by container" in error_output:
            import re
            container_match = re.search(r'The container name "([^"]+)"', error_output)
            container_name = container_match.group(1) if container_match else None
            raise DockerContainerConflictError(container_name) from e
        raise

def find_free_port(start_port: int = 8000) -> int:
    """Ищет свободный порт, начиная с указанного"""
    port = start_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError("Нет свободных портов! Ахуеть!")

def get_available_port(default_port: int) -> int:
    port = default_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError(f"Не могу найти свободный порт после {default_port}")

def is_port_free(port: int) -> bool:
    """Проверяет свободен ли порт"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except OSError:
        return False

def get_port(service: str) -> int:
    """Получает порт из переменных окружения или использует значение по умолчанию"""
    service_upper = service.upper().replace('_PORT', '')
    return int(os.getenv(service, DEFAULT_PORTS[service_upper]))

def check_service(name: str, port: int, retries: int = 5, delay: int = 2) -> bool:
    """Базовая функция проверки сервиса"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for _ in range(retries):
        try:
            sock.connect(('localhost', port))
            sock.close()
            return True
        except:
            print(f"⏳ Ждём {name} на порту {port}...")
            time.sleep(delay)
    return False

def check_services():
    """Проверяет доступность всех сервисов"""
    services_config = {
        'Redis': ('REDIS_PORT', 5),
        'RabbitMQ': ('RABBITMQ_UI_PORT', 5),
        'PostgreSQL': ('POSTGRES_PORT', 30),
    }

    for service_name, (port_key, retries) in services_config.items():
        port = get_port(port_key)
        if not check_service(service_name, port, retries):
            print(f"❌ {service_name} не доступен на порту {port}!")
            return False
    return True

def get_postgres_container_name() -> str:
    """
    Находит имя контейнера PostgreSQL или возвращает стандартное имя

    Returns:
        str: Имя контейнера PostgreSQL или стандартное имя
    """
    try:
        # Проверяем, доступен ли Docker
        which_result = subprocess.run(
            ["which", "docker"],
            capture_output=True,
            text=True
        )
        if which_result.returncode != 0:
            print("ℹ️ Docker не найден, используем прямое подключение к PostgreSQL")
            return "postgres"  # Стандартное имя для прямого подключения

        result = subprocess.run(
            ["docker", "ps", "--filter", "name=postgres", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        containers = [name for name in result.stdout.strip().split('\n') if name]
        if not containers:
            print("⚠️ Контейнер PostgreSQL не найден через Docker, используем прямое подключение")
            return "postgres"
        return containers[0]  # Берем первый найденный контейнер
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Ошибка при поиске контейнера PostgreSQL через Docker: {e}")
        return "postgres"
    except Exception as e:
        print(f"⚠️ Непредвиденная ошибка: {e}")
        return "postgres"

def create_database():
    """
    Создание базы данных, если она не существует
    """
    print("🛠️ Проверяем наличие базы данных...")

    # Получаем данные из переменных окружения
    db_config = load_env_vars()

    # Получаем имя контейнера PostgreSQL динамически
    postgres_container = get_postgres_container_name()
    print(f"🔍 Используем PostgreSQL: {postgres_container}")

    # Извлекаем настройки БД
    user = db_config.get('POSTGRES_USER', 'postgres')
    password = db_config.get('POSTGRES_PASSWORD', '')
    host = db_config.get('POSTGRES_HOST', 'localhost')
    port = db_config.get('POSTGRES_PORT', '5432')
    db_name = db_config.get('POSTGRES_DB', 'aichat_db')

    try:
        # Проверяем, доступен ли Docker
        which_docker = subprocess.run(["which", "docker"], capture_output=True)
        docker_available = which_docker.returncode == 0

        if docker_available:
            # Метод с использованием Docker
            check_db_inside = subprocess.run(
                ["docker", "exec", "-i", postgres_container, "psql", "-U", user, "-c",
                f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';"],
                capture_output=True, text=True
            )

            if "1 row" not in check_db_inside.stdout:
                print(f"🛠️ База данных {db_name} не найдена внутри контейнера, создаём...")
                create_cmd = [
                    "docker", "exec", "-i", postgres_container, "psql", "-U", user, "-c",
                    f"CREATE DATABASE {db_name};"
                ]
                subprocess.run(create_cmd, check=True)
                print(f"✅ База данных {db_name} создана внутри контейнера!")
            else:
                print(f"✅ База данных {db_name} существует внутри контейнера!")
        else:
            # Прямое подключение через psql
            print(f"🔄 Проверяем БД напрямую через psql...")

            # Формируем команду для проверки существования БД
            psql_command = f"psql -U {user} -h {host} -p {port}"
            if password:
                # Установка переменной окружения PGPASSWORD для передачи пароля
                env = os.environ.copy()
                env["PGPASSWORD"] = password
            else:
                env = os.environ.copy()

            # Проверяем существование БД
            check_db = subprocess.run(
                f"{psql_command} -c \"SELECT 1 FROM pg_database WHERE datname = '{db_name}';\"",
                shell=True, env=env, capture_output=True, text=True
            )

            if "1 row" not in check_db.stdout:
                print(f"🛠️ База данных {db_name} не найдена, создаём...")
                create_cmd = f"{psql_command} -c \"CREATE DATABASE {db_name};\""
                subprocess.run(create_cmd, shell=True, env=env, check=True)
                print(f"✅ База данных {db_name} создана!")
            else:
                print(f"✅ База данных {db_name} существует!")

        # Выводим информацию о подключении
        dsn = f"postgresql://{user}:*******@{host}:{port}/{db_name}"
        print(f"🔄 Информация о подключении к БД: {dsn} (пароль скрыт)")

        return True
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        return False


def start_infrastructure():
    print("🚀 Запускаем инфраструктуру...")

    env_vars = load_env_vars()

    busy_ports = []
    for service, default_port in DEFAULT_PORTS.items():
        # Получаем порт из .env.dev или используем дефолтный
        port = int(env_vars.get(f"{service}_PORT", default_port))
        if not is_port_free(port):
            busy_ports.append(f"{service}: {port}")

    if busy_ports:
        print("❌ Следующие порты заняты:")
        for port_info in busy_ports:
            print(f"   - {port_info}")
        print("💡 Останови процессы на этих портах или измени порты в .env.dev")
        return False

    try:
        # Проверяем статус Docker
        try:
            docker_info = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Docker запущен и работает")
        except subprocess.CalledProcessError as e:
            print("❌ Проблема с Docker:")
            if "permission denied" in str(e.stderr).lower():
                print("💡 Нет прав доступа к Docker. Попробуйте запустить от администратора.")
            elif "cannot connect to the docker daemon" in str(e.stderr).lower():
                print("💡 Docker Daemon не отвечает. Проверьте что:")
                print("   1. Docker Desktop точно запущен")
                print("   2. Служба Docker Engine работает")
                print("   3. Нет конфликтов с WSL или другими службами")
            raise DockerDaemonNotRunningError()

        # Проверяем запущенные контейнеры
        print("🔍 Проверяем запущенные контейнеры...")
        ps_result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        if ps_result.stdout.strip():
            print("⚠️ Найдены запущенные контейнеры:")
            for container in ps_result.stdout.strip().split('\n'):
                print(f"   - {container}")

        # Убиваем все контейнеры
        try:
            run_compose_command("down --remove-orphans")
        except subprocess.CalledProcessError as e:
            error_output = str(e)
            if "docker daemon is not running" in error_output or "pipe/docker_engine" in error_output:
                raise DockerDaemonNotRunningError()
            raise

        # Очищаем тома
        try:
            subprocess.run(["docker", "volume", "prune", "-f"], check=True)
        except subprocess.CalledProcessError as e:
            error_output = str(e)
            if "docker daemon is not running" in error_output or "pipe/docker_engine" in error_output:
                raise DockerDaemonNotRunningError()
            raise

        # Получаем свободные порты
        ports = {
            service: get_available_port(default_port)
            for service, default_port in DEFAULT_PORTS.items()
        }

        # Используем порты в docker-compose через переменные окружения
        env = {
            f"{service}_PORT": str(port)
            for service, port in ports.items()
        }

        try:
            run_compose_command(["up", "-d"], COMPOSE_FILE_WITHOUT_BACKEND, env=env)
        except subprocess.CalledProcessError as e:
            error_output = str(e)
            if "docker daemon is not running" in error_output or "pipe/docker_engine" in error_output:
                raise DockerDaemonNotRunningError()
            elif "Conflict" in error_output and "is already in use by container" in error_output:
                # Извлекаем имя контейнера из сообщения об ошибке
                import re
                container_match = re.search(r'The container name "([^"]+)"', error_output)
                container_name = container_match.group(1) if container_match else None
                raise DockerContainerConflictError(container_name)
            raise

        # Ждем доступности сервисов
        check_services()

        # Запускаем миграции после успешного поднятия PostgreSQL
        print("📦 Запускаем миграции...")
        migrate()
        print("✅ Миграции выполнены!")

        print("\n🔗 Доступные адреса:")
        print(f"📊 FastAPI Swagger:    http://localhost:{ports['FASTAPI']}/docs")
        print(f"🐰 RabbitMQ UI:       http://localhost:{ports['RABBITMQ_UI']}")
        print(f"🗄️ PostgreSQL:        localhost:{ports['POSTGRES']}")
        print(f"📦 Redis:             localhost:{ports['REDIS']}")
        print(f"🔍 PgAdmin:           http://localhost:{ports['PGADMIN']}")
        print(f"📊 Redis Commander:    http://localhost:{ports['REDIS_COMMANDER']}")

        print("✅ Инфраструктура готова!")
        return True
    except DockerDaemonNotRunningError as e:
        print(f"❌ {e}")
        print("💡 Запусти Docker Desktop и попробуй снова, олух.")
        return False
    except DockerContainerConflictError as e:
        print(f"❌ {e}")
        print("💡 Выполни следующую команду для удаления конфликтующих контейнеров:")
        print("```")
        print("docker rm -f $(docker ps -aq)")
        print("```")
        return False
    except Exception as e:
        print(f"❌ Ошибка при запуске инфраструктуры: {e}")
        return False

def setup():
    """Настройка окружения"""
    system = platform.system()
    if system == "Windows":
        subprocess.run(["powershell", "-File", "scripts/setup.ps1"], check=True)
    else:
        subprocess.run(["bash", "scripts/setup.sh"], check=True)

def activate():
    """Активация окружения и запуск dev режима"""
    system = platform.system()
    if system == "Windows":
        subprocess.run(["powershell", "-File", "scripts/activate.ps1"], check=True)
    else:
        subprocess.run(["bash", "scripts/activate.sh"], check=True)

def dev(port: Optional[int] = None):
    """
    Запуск в режиме разработки

    Args:
        port: Конкретный порт для запуска. Если None - найдет свободный
    """

    # Запускаем инфраструктуру
    if not start_infrastructure():
        return

    if port is None:
        port = find_free_port()


    print(f"🚀 Запускаем сервер на порту {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="debug",
        access_log=False
    )

def serve(port: Optional[int] = None):
    """
    Запускает uvicorn сервер

    Args:
        port: Конкретный порт для запуска. Если None - найдет свободный
    """
    if port is None:
        port = find_free_port()

    print(f"🚀 Запускаем сервер на порту {port}")
    subprocess.run([
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--proxy-headers",
        "--forwarded-allow-ips=*"
    ], check=True)

def migrate():
    """
    Запуск миграций.
    """
    subprocess.run(["alembic", "upgrade", "head"], check=True)

def format():
    """
    Форматирование кода.
    """
    subprocess.run(["black", "app/"], check=True)
    subprocess.run(["isort", "app/"], check=True)

def check():
    """
    Проверка кода.
    """
    mypy_success = True
    flake8_success = True

    # Проверка mypy
    try:
        mypy_result = subprocess.run(
            ["mypy", "app/"],
            capture_output=True,
            text=True,
            check=True
        )
        mypy_errors = mypy_result.stdout.split('\n')

        mypy_error_groups = {
            'error: Incompatible': 'Несовместимые типы',
            'error: Name': 'Ошибки именования',
            'error: Missing': 'Отсутствующие типы',
            'error: Argument': 'Ошибки аргументов',
            'error: Return': 'Ошибки возвращаемых значений'
        }

        # Сначала собираем все ошибки в известные группы
        grouped_errors = set()
        for pattern, desc in mypy_error_groups.items():
            matches = [e for e in mypy_errors if pattern in e]
            if matches:
                print(f"\n🔍 MyPy - {desc}:")
                for error in matches:
                    print(f"- {error}")
                    grouped_errors.add(error)

        # Оставшиеся ошибки выводим как "Прочие"
        other_errors = [e for e in mypy_errors if e and e not in grouped_errors]
        if other_errors:
            print("\n🔍 MyPy - Прочие ошибки:")
            for error in other_errors:
                print(f"- {error}")
    except subprocess.CalledProcessError as e:
        print("❌ Найдены ошибки mypy:")
        print(e.stdout)
        mypy_success = False

    # Проверка flake8
    try:
        result = subprocess.run(
            ["flake8", "app/"],
            capture_output=True,
            text=True,
            check=True
        )
        flake8_errors = result.stdout.split('\n')

        # Группируем ошибки по типу
        error_groups = {
            'E501': 'Длинные строки',
            'F821': 'Неопределенные переменные',
            'F841': 'Неиспользуемые переменные',
            'W605': 'Некорректные escape-последовательности',
            'E262': 'Неправильные комментарии'
        }

        # Собираем известные ошибки
        grouped_errors = set()
        for code, desc in error_groups.items():
            matches = [e for e in flake8_errors if code in e]
            if matches:
                print(f"\n🔍 Flake8 - {desc}:")
                for error in matches:
                    print(f"- {error.split(':')[0]}")
                    grouped_errors.add(error)

        # Выводим оставшиеся ошибки
        other_errors = [e for e in flake8_errors if e and e not in grouped_errors]
        if other_errors:
            print("\n🔍 Flake8 - Прочие ошибки:")
            for error in other_errors:
                print(f"- {error.split(':')[0]}")

    except subprocess.CalledProcessError as e:
        print("❌ Найдены ошибки flake8: ")
        print(e.stdout)
        flake8_success = False

    return mypy_success and flake8_success

def lint():
    """
    Запуск линтера.
    """
    format()
    check()

def test():
    """
    Запуск тестов.
    """
    env = os.environ.copy()
    env["ENV_FILE"] = ".env.test"
    try:
        subprocess.run(
            ["pytest", "tests/", "-v"],
            env=env,
            check=True
        )
    except subprocess.CalledProcessError:
        pass

def start_all():
    """Запускает миграции и сервер"""
    migrate()
    serve()
