import asyncio
import socket
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Network & Web Vulnerability Scanner API")

# Разрешаем мобильному приложению подключаться к нашему серверу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Функция для асинхронной проверки одного порта
async def scan_single_port(ip: str, port: int, timeout: float = 1.0):
    try:
        # Открываем сокет-соединение
        conn = asyncio.open_connection(ip, port)
        # Ждем ответа в пределах тайм-аута
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return port, True
    except:
        return port, False


# 1. ЭНДПОИНТ: Сканирование портов (Network Scan)
@app.get("/api/scan/network")
async def scan_network(target_ip: str):
    # Список наиболее критичных портов для проверки
    common_ports = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 3306, 3389, 8080]

    # Описания портов для вывода красивых рекомендаций на мобилке
    port_descriptions = {
        21: "FTP (Передача файлов. Часто передает пароли в открытом виде)",
        22: "SSH (Удаленный доступ. Проверьте на стойкость пароля)",
        23: "Telnet (Устаревший незащищенный протокол удаленного доступа!)",
        80: "HTTP (Веб-сервер. Трафик не шифруется)",
        443: "HTTPS (Защищенный веб-сервер)",
        445: "SMB (Сетевые папки. Уязвима к атакам типа EternalBlue, если ОС устарела)",
        3306: "MySQL (База данных. Опасно оставлять открытой в интернет)",
        3389: "RDP (Удаленный рабочий стол Windows. Мишень для брутфорса)"
    }

    try:
        # Валидация IP-адреса
        socket.gethostbyname(target_ip)
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Неверный IP-адрес или хост")

    # Запускаем проверку всех портов одновременно (асинхронно)
    tasks = [scan_single_port(target_ip, port) for port in common_ports]
    results = await asyncio.gather(*tasks)

    open_ports = []
    for port, is_open in results:
        if is_open:
            open_ports.append({
                "port": port,
                "status": "Открыт",
                "description": port_descriptions.get(port, "Неизвестный сервис / Альтернативный порт")
            })

    return {
        "target": target_ip,
        "open_ports_count": len(open_ports),
        "scan_results": open_ports
    }


# 2. ЭНДПОИНТ: Пассивный анализ сайта (Web Scan)
@app.get("/api/scan/web")
def scan_web(url: str):
    # Добавляем протокол, если пользователь забыл его ввести
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        # Делаем запрос к сайту с таймаутом в 5 секунд
        response = requests.get(url, timeout=5, headers={"User-Agent": "SecApp-Student-Project/1.0"})
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Не удалось получить доступ к сайту: {str(e)}")

    headers = response.headers
    vulnerabilities = []

    # 1. Проверяем заголовок защиты от кликджекинга (Clickjacking)
    if "X-Frame-Options" not in headers:
        vulnerabilities.append({
            "type": "Missing X-Frame-Options",
            "severity": "Medium",
            "description": "Сайт можно встроить внутрь чужого сайта через iframe. Это позволяет злоумышленникам перехватывать клики пользователей (Кликджекинг)."
        })

    # 2. Проверяем строгую политику безопасности контента (CSP)
    if "Content-Security-Policy" not in headers:
        vulnerabilities.append({
            "type": "Missing Content-Security-Policy (CSP)",
            "severity": "High",
            "description": "Отсутствует защита от XSS-атак. Злоумышленник может внедрить вредоносный JS-скрипт на страницу."
        })

    # 3. Проверяем принудительный HTTPS (HSTS)
    if "Strict-Transport-Security" not in headers:
        vulnerabilities.append({
            "type": "Missing HSTS",
            "severity": "Low",
            "description": "Сайт не требует от браузера использовать исключительно защищенное HTTPS-соединение, что делает возможным перехват трафика (MitM)."
        })

    # 4. Проверяем утечку информации о сервере
    server_info = headers.get("Server", "Скрыто")
    x_powered_by = headers.get("X-Powered-By", None)

    if x_powered_by or ("Server" in headers and len(server_info) > 10):
        vulnerabilities.append({
            "type": "Information Disclosure",
            "severity": "Low",
            "description": f"Сервер раскрывает информацию о технологиях ({server_info} {x_powered_by or ''}). Хакеру проще подобрать эксплойт под конкретную версию ПО."
        })

    return {
        "url": url,
        "status_code": response.status_code,
        "vulnerabilities_found": len(vulnerabilities),
        "vulnerabilities": vulnerabilities
    }
