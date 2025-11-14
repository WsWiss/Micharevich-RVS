#!/usr/bin/env python3
import socket
import threading
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5000
ENC = 'utf-8'

clients = {}          # {socket: nickname}
lock = threading.Lock()


def broadcast(msg: str, sender=None):
    """Послать строку всем, кроме sender."""
    with lock:
        for sock in list(clients):
            if sock != sender:
                try:
                    sock.sendall(msg.encode(ENC))
                except OSError:
                    # сокет уже мёртв – уберём позже
                    pass


def handle(client: socket.socket, addr):
    """Обслуживает одного клиента в отдельном потоке."""
    # Первое сообщение – ник
    try:
        nick = client.recv(1024).decode(ENC).strip()
        if not nick:
            raise ValueError("Empty nick")
    except Exception as e:
        print(f"[{datetime.now()}][{addr}] ошибка при получении ника: {e}")
        client.close()
        return

    with lock:
        clients[client] = nick
    print(f"[{datetime.now()}][+] {nick} подключился. Всего: {len(clients)}")
    broadcast(f"\n-----------------------------\n[Система] {nick} вошёл в чат\n-----------------------------\n")
    # Основной цикл приёма сообщений
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            text = data.decode(ENC).strip()
            if text.lower() == 'exit':
                break
            broadcast(f"{nick}: {text}", sender=client)
            print(f"[{datetime.now()}][{nick}] Сообщение отправлено: {text}")
        except Exception:
            break

    # Отключение
    with lock:
        clients.pop(client, None)
    print(f"[{datetime.now()}][-] {nick} отключился. Всего: {len(clients)}")
    broadcast(f"[{datetime.now()}][Система] {nick} покинул чат")
    client.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"Сервер запущен на {HOST}:{PORT}")

        while True:
            conn, addr = srv.accept()
            threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


if __name__ == '__main__':
    main()