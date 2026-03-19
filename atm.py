import random

# ---------------------------
# Helpers
# ---------------------------
def generate_iban(used_ibans):
    while True:
        check_digits = str(random.randint(10, 99))
        body = "".join(str(random.randint(0, 9)) for _ in range(22))
        iban = "TR" + check_digits + body
        if iban not in used_ibans:
            used_ibans.add(iban)
            return iban


def find_user_by_iban(users, target_iban):
    for username, data in users.items():
        if data["iban"] == target_iban:
            return username
    return None


def money_input(prompt):
    s = input(prompt).strip()
    s = s.replace(",", ".")

    if s == "":
        return None

    if s.count(".") > 1:
        return None

    parts = s.split(".")
    if not all(p.isdigit() for p in parts):
        return None

    return float(s)


# ---------------------------
# Auth
# ---------------------------
def register(users, used_ibans):
    print("\n--- Kayıt Ol ---")
    username = input("Kullanıcı adı: ").strip()

    if username == "":
        print("Kullanıcı adı boş olamaz.")
        return None

    if username in users:
        print("Bu kullanıcı adı zaten var.")
        return None

    password = input("Şifre: ").strip()
    if len(password) < 4:
        print("Şifre en az 4 karakter olmalı.")
        return None

    iban = generate_iban(used_ibans)

    users[username] = {
        "password": password,
        "balance": 0.0,
        "iban": iban,
        "history": []
    }

    print(f"Kayıt başarılı! IBAN: {iban}")
    return username


def login(users):
    print("\n--- Giriş Yap ---")
    username = input("Kullanıcı adı: ").strip()
    password = input("Şifre: ").strip()

    if username not in users:
        print("Kullanıcı bulunamadı.")
        return None

    if users[username]["password"] != password:
        print("Şifre yanlış.")
        return None

    print("Giriş başarılı.")
    return username


def change_password(user):
    print("\n--- Şifre Değiştir ---")
    old_pw = input("Mevcut şifre: ").strip()

    if old_pw != user["password"]:
        print("Mevcut şifre yanlış.")
        return

    new_pw = input("Yeni şifre: ").strip()
    if len(new_pw) < 4:
        print("Yeni şifre en az 4 karakter olmalı.")
        return

    user["password"] = new_pw
    print("Şifre güncellendi.")


# ---------------------------
# Banking operations
# ---------------------------
def deposit(user, amount, note=""):
    if amount is None or amount <= 0:
        print("Geçersiz tutar.")
        return

    user["balance"] += amount
    user["history"].append(("DEPOSIT", amount, user["balance"], note))
    print(f"Para yatırıldı. Yeni bakiye: {user['balance']:.2f}")


def withdraw(user, amount, note=""):
    if amount is None or amount <= 0:
        print("Geçersiz tutar.")
        return

    if amount > user["balance"]:
        print("Yetersiz bakiye.")
        return

    user["balance"] -= amount
    user["history"].append(("WITHDRAW", amount, user["balance"], note))
    print(f"Para çekildi. Yeni bakiye: {user['balance']:.2f}")


def transfer(users, sender_username, target_iban, amount):
    sender = users[sender_username]

    if amount is None or amount <= 0:
        print("Geçersiz tutar.")
        return

    if amount > sender["balance"]:
        print("Yetersiz bakiye.")
        return

    if target_iban == sender["iban"]:
        print("Kendi IBAN'ına transfer yapamazsın.")
        return

    receiver_username = find_user_by_iban(users, target_iban)
    if receiver_username is None:
        print("Hedef IBAN bulunamadı.")
        return

    receiver = users[receiver_username]

    # gönder
    sender["balance"] -= amount
    sender["history"].append(("TRANSFER_OUT", amount, sender["balance"], f"to:{target_iban}"))

    # alıcı
    receiver["balance"] += amount
    receiver["history"].append(("TRANSFER_IN", amount, receiver["balance"], f"from:{sender['iban']}"))

    print(f"Transfer başarılı. Yeni bakiye: {sender['balance']:.2f}")


def print_history(user):
    print("\n--- İşlem Geçmişi ---")
    history = user["history"]

    if len(history) == 0:
        print("Henüz işlem yok.")
        return

    for i, item in enumerate(history, start=1):
        ttype, amount, new_balance, note = item
        note_text = f" | Not: {note}" if note else ""
        print(f"{i}) {ttype} | Tutar: {amount:.2f} | Bakiye: {new_balance:.2f}{note_text}")


def report(user):
    print("\n--- Rapor ---")
    history = user["history"]

    if len(history) == 0:
        print("Rapor için işlem yok.")
        return

    deposits = [h for h in history if h[0] == "DEPOSIT"]
    withdraws = [h for h in history if h[0] == "WITHDRAW"]
    out_transfers = [h for h in history if h[0] == "TRANSFER_OUT"]
    in_transfers = [h for h in history if h[0] == "TRANSFER_IN"]

    deposit_amounts = list(map(lambda x: x[1], deposits))
    withdraw_amounts = list(map(lambda x: x[1], withdraws))

    total_deposit = sum(deposit_amounts) if deposit_amounts else 0
    total_withdraw = sum(withdraw_amounts) if withdraw_amounts else 0

    print(f"Toplam yatırma: {total_deposit:.2f}")
    print(f"Toplam çekme: {total_withdraw:.2f}")
    print(f"Transfer gönderim sayısı: {len(out_transfers)}")
    print(f"Transfer alım sayısı: {len(in_transfers)}")

    big_ops = list(filter(lambda h: h[1] >= 1000, history))
    print(f"Büyük işlem adedi (>=1000): {len(big_ops)}")

    if big_ops:
        print("Örnek büyük işlemler:")
        for item in big_ops[:3]:
            print(f"- {item[0]} | {item[1]:.2f} | Not: {item[3]}")


# ---------------------------
# Menu
# ---------------------------
def atm_menu(users, username):
    user = users[username]

    while True:
        print("\n======================")
        print(f"Kullanıcı: {username} | IBAN: {user['iban']}")
        print("1) Bakiye")
        print("2) Para Yatır")
        print("3) Para Çek")
        print("4) Havale")
        print("5) Geçmiş")
        print("6) Rapor")
        print("7) Şifre Değiştir")
        print("0) Çıkış")

        choice = input("Seçim: ").strip()

        if choice == "1":
            print(f"Bakiye: {user['balance']:.2f}")

        elif choice == "2":
            deposit(user, money_input("Tutar: "), input("Not: "))

        elif choice == "3":
            withdraw(user, money_input("Tutar: "), input("Not: "))

        elif choice == "4":
            transfer(users, username, input("IBAN: ").upper(), money_input("Tutar: "))

        elif choice == "5":
            print_history(user)

        elif choice == "6":
            report(user)

        elif choice == "7":
            change_password(user)

        elif choice == "0":
            break

        else:
            print("Hatalı seçim")


# ---------------------------
# Main
# ---------------------------
def main():
    users = {}
    used_ibans = set()

    # demo
    demo_iban = generate_iban(used_ibans)
    users["demo"] = {
        "password": "1234",
        "balance": 500,
        "iban": demo_iban,
        "history": []
    }

    while True:
        print("\n=== MINI ATM ===")
        print("1) Kayıt")
        print("2) Giriş")
        print("0) Çıkış")

        choice = input("Seçim: ")

        if choice == "1":
            u = register(users, used_ibans)
            if u:
                atm_menu(users, u)

        elif choice == "2":
            u = login(users)
            if u:
                atm_menu(users, u)

        elif choice == "0":
            break


if __name__ == "__main__":
    main()