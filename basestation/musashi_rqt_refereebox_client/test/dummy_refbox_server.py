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
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[DummyRefBox] Listening on {HOST}:{PORT}")
    client_socket, client_addr = server_socket.accept()
    print(f"[DummyRefBox] Client connected from {client_addr}")

    # 接続直後に簡単な応答を返す
    msg = json.dumps({"status": "connected"}) + '\0'
    client_socket.sendall(msg.encode('utf-8'))
    print(f"[DummyRefBox] Sent: {msg}")

    # WELCOMコマンドを送信
    welcom_msg = json.dumps({"command": "WELCOM", "targetTeam": "224.16.32.44"}) + '\0'
    client_socket.sendall(welcom_msg.encode('utf-8'))
    print(f"[DummyRefBox] Sent: {welcom_msg}")

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
        {"command": "START", "targetTeam": ""},
        {"command": "STOP", "targetTeam": ""},
        {"command": "DROP_BALL", "targetTeam": ""},
        {"command": "HALF_TIME", "targetTeam": ""},
        {"command": "END_GAME", "targetTeam": ""},
        {"command": "GAME_OVER", "targetTeam": ""},
        {"command": "PARK", "targetTeam": ""},
        {"command": "FIRST_HALF", "targetTeam": ""},
        {"command": "SECOND_HALF", "targetTeam": ""},
        {"command": "FIRST_HALF_OVERTIME", "targetTeam": ""},
        {"command": "SECOND_HALF_OVERTIME", "targetTeam": ""},
        {"command": "RESET", "targetTeam": ""},
        {"command": "KICKOFF", "targetTeam": "224.16.32.44"},
        {"command": "FREEKICK", "targetTeam": "224.16.32.44"},
        {"command": "GOALKICK", "targetTeam": "224.16.32.44"},
        {"command": "THROWIN", "targetTeam": "224.16.32.44"},
        {"command": "CORNER", "targetTeam": "224.16.32.44"},
        {"command": "PENALTY", "targetTeam": "224.16.32.44"},
        {"command": "GOAL", "targetTeam": "224.16.32.44"},
        {"command": "SUBGOAL", "targetTeam": "224.16.32.44"},
        {"command": "REPAIR", "targetTeam": "224.16.32.44"},
        {"command": "YELLOW_CARD", "targetTeam": "224.16.32.44"},
        {"command": "DOUBLE_YELLOW", "targetTeam": "224.16.32.44"},
        {"command": "RED_CARD", "targetTeam": "224.16.32.44"},
        {"command": "SUBSTITUTION", "targetTeam": "224.16.32.44"},
        {"command": "IS_ALIVE", "targetTeam": "224.16.32.44"},
    ]
    print("\n--- Command Templates ---")
    for i, t in enumerate(templates, 1):
        print(f"  {i}: {t}")
    print("  0: 任意のJSONを手入力")
    print("------------------------\n")
    # commandでtargetTeam空文字にするリスト
    empty_team_commands = [
        "START", "STOP", "DROP_BALL", "HALF_TIME", "END_GAME", "GAME_OVER", "PARK",
        "FIRST_HALF", "SECOND_HALF", "FIRST_HALF_OVERTIME", "SECOND_HALF_OVERTIME", "RESET"
    ]
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
            else:
                try:
                    obj = json.loads(sel)
                except Exception as e:
                    print(f"Invalid JSON: {e}")
                    continue

            # commandが指定リストならtargetTeamを空文字に
            if isinstance(obj, dict) and obj.get("command") in empty_team_commands:
                obj["targetTeam"] = ""

            msg = json.dumps(obj) + '\0'
            client_socket.sendall(msg.encode('utf-8'))
            print(f"[DummyRefBox] Sent: {msg}")
    finally:
        client_socket.close()
        server_socket.close()
        print("[DummyRefBox] Server stopped.")

if __name__ == '__main__':
    main()
