import asyncio
from asyncio import transports


# управление соединенияем
# asyncio.Protocol - инструментарий для кодирования сообщений;
class ServerProtocol(asyncio.Protocol):  # - класс опишет передачу данных;
    """ принимать данные, формировать, кодировать и оптравлять клиенту назад"""
    login: str = None
    server: 'Server'  # ссылка на сервер - чтобы отключиться, покдлючиться и т.д..
    # тип сервера, не существующий на данный момент (выше);
    transport: transports.Transport
    """далее логика отправки получения и декодирования сообщений"""
    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes) -> None:
        print(data.decode())

        decoded = data.decode()

        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")
                self.transport.write(
                    f"Привет, {self.login}!\n".encode()
                )
            else:
                self.transport.write("Неправильный логин\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print('Клиент вышел')

    def send_message(self, content: str):
        message = f"{self.login}: {content}\n"

        for user in self.server.clients:
            user.transport.write(message.encode())


# соединение между сервером и клиентом (постояяно создается на каждого нового подключившегося клиента)
class Server:
    clients: list

    def __init__(self):
        self.clients = []  # - при старте сервера список клиентов пустой;

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()  # - получаем асинхронное управление и получаем асинхронный сервер;

        coroutine = await loop.create_server(
            self.build_protocol,  # - конструктор протокола (верхнего класса)
            '127.0.0.1',  # - хост - пока домашний айпишник;
            8888  # - хост - частота на которой находяться потоки сообщений; больше 1024 (до - занято)
        )

        print("Сервер запущен ...")
        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")

# протокол - набор правил и стандартов, как выглядит сообщение и т.д..
# 1 - отправлять мы можем только байты и принимать мы можем только байты; внутри байта уже может быть  что угодно
# (стикер, фото и т. д..)

# есть два протокола - udp - передача графики потоковой, онлайн трансляции, рассылки;
# для мессенджеров и т.д.. есть протокол с большей гарантией доставки - ttp; минус - скорость поменьше;

# pyside2-uic app/interface.ui -o app/interface.py - для конвертации интерфейса
