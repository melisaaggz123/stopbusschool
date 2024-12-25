import sqlite3

# Veritabanı bağlantısı
def get_db_connection():
    conn = sqlite3.connect('okul_servis_sistemi2.db')
    conn.row_factory = sqlite3.Row
    return conn

# Öğrenci Modeli
class Ogrenci:
    def __init__(self, ogrenciID, sifre, email=None):
        self.ogrenciID = ogrenciID
        self.sifre = sifre
        self.email = email

    @staticmethod
    def giris(conn, ogrenciID, sifre):
        """
        Öğrenci girişini kontrol eden metod.
        """
        query = 'SELECT * FROM Ogrenciler WHERE ogrenciID = ? AND sifre = ?'
        ogrenci = conn.execute(query, (ogrenciID, sifre)).fetchone()
        return ogrenci

    def kayit(self, conn):
        """
        Öğrenciyi veritabanına kaydeden metod.
        """
        query = 'INSERT INTO Ogrenciler (ogrenciID, sifre, email) VALUES (?, ?, ?)'
        conn.execute(query, (self.ogrenciID, self.sifre, self.email))
        conn.commit()

# Öğretmen Modeli
class Ogretmen:
    def __init__(self, ogretmenID, sifre, email=None):
        self.ogretmenID = ogretmenID
        self.sifre = sifre
        self.email = email

    @staticmethod
    def giris(conn, ogretmenID, sifre):
        """
        Öğretmen girişini kontrol eden metod.
        """
        query = 'SELECT * FROM Ogretmenler WHERE ogretmenID = ? AND sifre = ?'
        ogretmen = conn.execute(query, (ogretmenID, sifre)).fetchone()
        return ogretmen

    def kayit(self, conn):
        """
        Öğretmeni veritabanına kaydeden metod.
        """
        query = 'INSERT INTO Ogretmenler (ogretmenID, sifre, email) VALUES (?, ?, ?)'
        conn.execute(query, (self.ogretmenID, self.sifre, self.email))
        conn.commit()

# Yönetici Modeli (Admin)
class Yonetici:
    def __init__(self, yoneticiID, sifre, email=None):
        self.yoneticiID = yoneticiID
        self.sifre = sifre
        self.email = email

    @staticmethod
    def giris(conn, yoneticiID, sifre):
        """
        Yönetici girişini kontrol eden metod.
        """
        query = 'SELECT * FROM Yoneticiler WHERE yoneticiID = ? AND sifre = ?'
        yonetici = conn.execute(query, (yoneticiID, sifre)).fetchone()
        return yonetici

    def kayit(self, conn):
        """
        Yöneticiyi veritabanına kaydeden metod.
        """
        query = 'INSERT INTO Yoneticiler (yoneticiID, sifre, email) VALUES (?, ?, ?)'
        conn.execute(query, (self.yoneticiID, self.sifre, self.email))
        conn.commit()

# Şoför Modeli (Driver)
class Sofor:
    def __init__(self, soforID, sifre, email=None):
        self.soforID = soforID
        self.sifre = sifre
        self.email = email

    @staticmethod
    def giris(conn, soforID, sifre):
        """
        Şoför girişini kontrol eden metod.
        """
        query = 'SELECT * FROM Soforler WHERE soforID = ? AND sifre = ?'
        sofor = conn.execute(query, (soforID, sifre)).fetchone()
        return sofor

    def kayit(self, conn):
        """
        Şoförü veritabanına kaydeden metod.
        """
        query = 'INSERT INTO Soforler (soforID, sifre, email) VALUES (?, ?, ?)'
        conn.execute(query, (self.soforID, self.sifre, self.email))
        conn.commit()

#Ders Programı
class DersProgrami:
    def __init__(self, dersID=None, gun=None, saat=None, ders_adi=None):
        self.dersID = dersID
        self.gun = gun
        self.saat = saat
        self.ders_adi = ders_adi

    @staticmethod
    def tum_dersleri_getir(conn):
        """
        Tüm ders programını getirir.
        """
        query = 'SELECT * FROM DersProgrami'
        return conn.execute(query).fetchall()

    def ders_ekle(self, conn):
        """
        Yeni bir ders ekler.
        """
        query = 'INSERT INTO DersProgrami (gun, saat, ders_adi) VALUES (?, ?, ?)'
        conn.execute(query, (self.gun, self.saat, self.ders_adi))
        conn.commit()

    def ders_guncelle(self, conn):
        """
        Mevcut bir dersi günceller.
        """
        query = 'UPDATE DersProgrami SET gun = ?, saat = ?, ders_adi = ? WHERE dersID = ?'
        conn.execute(query, (self.gun, self.saat, self.ders_adi, self.dersID))
        conn.commit()

    @staticmethod
    def ders_sil(conn, dersID):
        """
        Bir dersi siler.
        """
        query = 'DELETE FROM DersProgrami WHERE dersID = ?'
        conn.execute(query, (dersID,))
        conn.commit()

# Duraklar
class Durak:
    def __init__(self, durakID=None, durak_adi=None):
        self.durakID = durakID
        self.durak_adi = durak_adi

    @staticmethod
    def tum_duraklari_getir(conn):
        query = 'SELECT * FROM Duraklar'
        return conn.execute(query).fetchall()

#Katılım
class KatilimDurumu:
    def __init__(self, ogrenciID, dersID, katilim, durakID=None):
        self.ogrenciID = ogrenciID
        self.dersID = dersID
        self.katilim = katilim
        self.durakID = durakID

    def kayit_ekle(self, conn):
        query = '''
        INSERT INTO KatilimDurumu (ogrenciID, dersID, katilim, durakID)
        VALUES (?, ?, ?, ?)
        '''
        conn.execute(query, (self.ogrenciID, self.dersID, self.katilim, self.durakID))
        conn.commit()


