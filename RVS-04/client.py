#!/usr/bin/env python3
import socket
import threading
import sys
import os

HOST = '127.0.0.1'
PORT = 5000
ENC  = 'utf-8'

# ---------- терминальные утилиты ----------
def clear_line():
    sys.stdout.write('\r\033[K')

def move_down():
    sys.stdout.write('\n')

def rewrite_prompt(nick):
    clear_line()
    sys.stdout.write(f'{nick}: ')
    sys.stdout.flush()

def receive_loop(sock, nick):
    while True:
        try:
            msg = sock.recv(1024).decode(ENC)
            if not msg:
                print('\rСервер разорвал соединение')
                os._exit(0)

            clear_line()
            print(msg)
            rewrite_prompt(nick)
        except OSError:
            os._exit(0)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        nick = input("Ваш ник: ").strip() or "anon"
        s.sendall(nick.encode(ENC))

        threading.Thread(target=receive_loop, args=(s, nick), daemon=True).start()

        rewrite_prompt(nick)
        while True:
            try:
                text = input()
            except KeyboardInterrupt:
                text = 'exit'
            if text.strip().lower() == 'exit':
                s.sendall(b'exit')
                break
            s.sendall(text.encode(ENC))
            rewrite_prompt(nick)

if __name__ == '__main__':
    main()