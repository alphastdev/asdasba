import requests, base64, os, zipfile, io

# === Ayarlar ===
GITHUB_API_URL = "https://api.github.com/repos/alphastdev/asdasba/contents/version.txt"
GITHUB_ZIP_URL = "https://github.com/alphastdev/asdasba/archive/refs/heads/main.zip"
LOCAL_VERSION_FILE = "version.txt"

def download_and_extract():
    """GitHub projesini indirir ve doğrudan bulunduğu klasöre çıkarır"""
    print("📦 Dosyalar indiriliyor...")
    try:
        r = requests.get(GITHUB_ZIP_URL, timeout=15)
        r.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            # Zip içindeki her dosyayı tek tek çıkarıyoruz
            for member in z.namelist():
                # İlk klasör adını (ör. "repo-main/") atla
                filename = member.split("/", 1)[-1]
                if not filename:
                    continue  # boşsa geç
                source = z.open(member)
                target_path = os.path.join(os.getcwd(), filename)

                # Klasör mü kontrol et
                if member.endswith("/"):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    # Alt klasörleri oluştur
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, "wb") as f:
                        f.write(source.read())

        print("✅ Dosyalar başarıyla çıkarıldı (direkt buraya).")
    except Exception as e:
        print(f"❌ İndirme/çıkarma hatası: {e}")

def get_remote_version():
    try:
        data = requests.get(GITHUB_API_URL, timeout=5).json()
        return base64.b64decode(data["content"]).decode().strip()
    except Exception as e:
        print(f"⚠️ Uzak versiyon alınamadı: {e}")
        return None

def get_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return None
    with open(LOCAL_VERSION_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def main():
    print("🔎 Güncelleme kontrolü yapılıyor...")
    remotev = get_remote_version()
    localv = get_local_version()

    if remotev is None:
        print("⚠️ Uzak versiyon okunamadı, işlem iptal.")
        return

    if not localv or remotev != localv:
        print(f"⬆️ Güncelleme gerekli ({localv} → {remotev})")
        download_and_extract()
    else:
        print("✅ Güncel (her şey tamam).")

if __name__ == "__main__":
    main()
