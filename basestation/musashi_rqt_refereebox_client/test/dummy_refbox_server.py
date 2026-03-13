"""
テスト用RefereeBoxサーバ（ダミー）
- clientからのTCP接続を待機
- 接続が確立されたら簡単な応答
- 任意のタイミングでコマンド（json）を送信可能
"""
import socket
import threading
import json

HOST = '0.0.0.0'  # すべてのインターフェースで待機
PORT = 28097      # 任意の空きポート


def main():
    """
    CUIアプリとして起動し、
    - サーバ起動
    - クライアント接続待機
    - 対話的にjsonコマンド送信
    を実現する。
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[DummyRefBox] Listening on {HOST}:{PORT}")
    client_socket, client_addr = server_socket.accept()
    print(f"[DummyRefBox] Client connected from {client_addr}")
    # 接続直後に簡単な応答を返す
    msg = json.dumps({"status": "connected"}) + '\0'
    client_socket.sendall(msg.encode('utf-8'))
    print(f"[DummyRefBox] Sent: {msg}")

    # 受信スレッド
    def recv_loop():
        while True:
            try:
                data = client_socket.recv(4096)
                if not data:
                    print("[DummyRefBox] Client disconnected")
                    break
                print(f"[DummyRefBox] Received: {data}")
            except Exception as e:
                print(f"[DummyRefBox] Error: {e}")
                break
    recv_thread = threading.Thread(target=recv_loop, daemon=True)
    recv_thread.start()

    # 対話的にコマンド送信
    templates = [
        {"command": "START", "targetTeam": "CYAN"},
        {"command": "STOP", "targetTeam": "CYAN"},
        {"command": "KICKOFF", "targetTeam": "MAGENTA"},
        {"command": "DROP_BALL", "targetTeam": "CYAN"},
    ]
    print("\n--- Command Templates ---")
    for i, t in enumerate(templates, 1):
        print(f"  {i}: {t}")
    print("  0: 任意のJSONを手入力")
    print("------------------------\n")
    try:
        while True:
            sel = input("番号選択 or JSON入力（'exit'で終了）: ")
            if sel.strip() == 'exit':
                break
            if sel.isdigit() and 0 <= int(sel) <= len(templates):
                idx = int(sel)
                if idx == 0:
                    cmd = input("JSONを入力: ")
                    try:
                        obj = json.loads(cmd)
                    except Exception as e:
                        print(f"Invalid JSON: {e}")
                        continue
                else:
                    obj = templates[idx-1]
                    # targetTeamだけ変更したい場合の補助
                    if 'targetTeam' in obj:
                        team = input(f"targetTeamを変更（Enterで現状維持: {obj['targetTeam']}）: ")
                        if team.strip():
                            obj = dict(obj)  # コピー
                            obj['targetTeam'] = team.strip()
            else:
                try:
                    obj = json.loads(sel)
                except Exception as e:
                    print(f"Invalid JSON: {e}")
                    continue
            msg = json.dumps(obj) + '\0'
            client_socket.sendall(msg.encode('utf-8'))
            print(f"[DummyRefBox] Sent: {msg}")
    finally:
        client_socket.close()
        server_socket.close()
        print("[DummyRefBox] Server stopped.")

if __name__ == '__main__':
    main()
