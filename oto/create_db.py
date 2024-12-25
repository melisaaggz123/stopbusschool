import sqlite3

# Veritabanı dosyasını oluştur (eğer yoksa)
conn = sqlite3.connect('okul_servis_sistemi2.db')
cursor = conn.cursor()

# Öğrenciler tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Ogrenciler (
    ogrenciID TEXT PRIMARY KEY,
    sifre TEXT NOT NULL,
    email TEXT
);
''')

# Öğretmenler tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Ogretmenler (
    ogretmenID TEXT PRIMARY KEY,
    sifre TEXT NOT NULL,
    email TEXT
);
''')

# Şoförler tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Soforler (
    soforID TEXT PRIMARY KEY,
    sifre TEXT NOT NULL,
    email TEXT
);
''')

# Yöneticiler tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Yoneticiler (
    yoneticiID TEXT PRIMARY KEY,
    sifre TEXT NOT NULL,
    email TEXT
);
''')

# Ders Programı tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS DersProgrami (
    dersID INTEGER PRIMARY KEY AUTOINCREMENT,
    gun TEXT NOT NULL,
    saat TEXT NOT NULL,
    ders_adi TEXT NOT NULL
);
''')

# Katılım Durumu tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS KatilimDurumu (
    ogrenciID TEXT NOT NULL,
    dersID INTEGER NOT NULL,
    katilim TEXT NOT NULL CHECK (katilim IN ('katil', 'katilmiyorum')), -- Katılım durumu kontrolü
    durakID INTEGER, -- Öğrencinin bineceği durak bilgisi
    PRIMARY KEY (ogrenciID, dersID), -- ogrenciID ve dersID birincil anahtar
    FOREIGN KEY (ogrenciID) REFERENCES Ogrenciler (ogrenciID),
    FOREIGN KEY (dersID) REFERENCES DersProgrami (dersID),
    FOREIGN KEY (durakID) REFERENCES Duraklar (durakID)
);
''')

# Duraklar tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Duraklar (
    durakID INTEGER PRIMARY KEY AUTOINCREMENT,
    durak_adi TEXT NOT NULL
);
''')

# Örnek durak verilerini ekle
duraklar = [
    ('Durak 1'),
    ('Durak 2'),
    ('Durak 3'),
    ('Durak 4'),
    ('Durak 5')
]
cursor.executemany('INSERT OR IGNORE INTO Duraklar (durak_adi) VALUES (?);', [(durak,) for durak in duraklar])

cursor.execute('''
CREATE TABLE IF NOT EXISTS Rotalar (
    rotaID INTEGER PRIMARY KEY AUTOINCREMENT,
    gun TEXT,
    saat TEXT,
    soforID INTEGER,
    durakID INTEGER,
    FOREIGN KEY(soforID) REFERENCES Soforler(soforID),
    FOREIGN KEY(durakID) REFERENCES Duraklar(durakID)
);
''')

# Veritabanı değişikliklerini kaydet
conn.commit()

# Bağlantıyı kapat
conn.close()

print("Veritabanı ve tablo başarıyla oluşturuldu!")
