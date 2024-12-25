from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import get_db_connection, Ogrenci, Ogretmen, Yonetici, Sofor
import sqlite3, secrets
import json



app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Güvenli bir şekilde rastgele bir anahtar oluşturur


# Ana Sayfa
@app.route('/')
def index():
    return render_template('anasayfa.html')

@app.route("/iletisim")
def iletisim():
    
    return render_template("iletisim.html")  # İletişim sayfası için bir şablon dosyası

@app.route("/hakkimizda")
def hakkimizda():
    return render_template("hakkimizda.html")  # İletişim sayfası için bir şablon dosyası

# Öğrenci Giriş
@app.route('/Giris/ogrenci_giris', methods=['GET', 'POST'])
def ogrenci_giris():
    error = None
    if request.method == 'POST':
        ogrenciID = request.form['ogrenciID']
        sifre = request.form['sifre']

        try:
            conn = get_db_connection()
            ogrenci = Ogrenci.giris(conn, ogrenciID, sifre)

            if ogrenci:
                session['ogrenciID'] = ogrenciID
                session['email'] = ogrenci['email']
                return redirect(url_for('ogrenci_islem'))
            else:
                error = "Geçersiz kullanıcı adı veya şifre."
        finally:
            conn.close()

    return render_template('Giris/ogrenci_giris.html', error=error)

# Öğrenci Kayıt
@app.route('/Kayit/ogrenci_kayit', methods=['GET', 'POST'])
def ogrenci_kayit():
    if request.method == 'POST':
        ogrenciID = request.form['ogrenciID']
        sifre = request.form['sifre']
        email = request.form['email']

        try:
            conn = get_db_connection()
            ogrenci = Ogrenci(ogrenciID, sifre, email)
            ogrenci.kayit(conn)
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Bu Öğrenci ID zaten kayıtlı!", 400
        finally:
            conn.close()

    return render_template('Kayit/ogrenci_kayit.html')

# Öğrenci İşlem Sayfası
@app.route('/Islemler/ogrenci_islem', methods=['GET', 'POST'])
def ogrenci_islem():
    if 'ogrenciID' not in session:
        return redirect(url_for('ogrenci_giris'))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

         # Ders programını veritabanından al
        cursor.execute("SELECT * FROM DersProgrami")
        ders_programi = cursor.fetchall()

        # Durak listesini çek
        cursor.execute("SELECT * FROM Duraklar")
        duraklar = cursor.fetchall()


        cursor.execute('''
            SELECT dersID, katilim FROM KatilimDurumu WHERE ogrenciID = ?''', (session['ogrenciID'],))
        katilim_durumlari = cursor.fetchall()
        katilim_dict = {durum[0]: durum[1] for durum in katilim_durumlari}


        if request.method == 'POST':
            action = request.form.get('action')  # İşlem türü ('katil' veya 'katilmiyorum')
            dersID = request.form.get('dersID')
            durak_id = request.form.get('durakID')  # Seçilen durak
            ogrenciID = session.get('ogrenciID')

            # Debug için ekrana yazdır
            print("Form verileri: ", durak_id, action, ogrenciID, dersID)

            # Eğer veriler alınamıyorsa:
            if not action :
                return "Form verileri eksik!", 400

            if action in ['katil', 'katilmiyorum']:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO KatilimDurumu (ogrenciID, dersID, katilim, durakID)
                        VALUES (?, ?, ?, ?);
                    ''', (ogrenciID, dersID, action, durak_id))
                    conn.commit()
                    print("Veri başarıyla eklendi.")
                except sqlite3.Error as e:
                    print(f"Veri eklenirken hata oluştu: {e}")
            
                return redirect(url_for('ogrenci_islem', dersID=dersID))

        return render_template('Islemler/ogrenci_islem.html', ders_programi=ders_programi, duraklar=duraklar, katilim_dict=katilim_dict)
    except Exception as e:
        return f"Hata oluştu: {e}"
    finally:
        conn.close()

# Öğretmen Giriş
@app.route('/Giris/ogretmen_giris', methods=['GET', 'POST'])
def ogretmen_giris():
    error = None
    if request.method == 'POST':
        ogretmenID = request.form['ogretmenID']
        sifre = request.form['sifre']

        try:
            conn = get_db_connection()
            ogretmen = Ogretmen.giris(conn, ogretmenID, sifre)

            if ogretmen:
                session['ogretmenID'] = ogretmenID
                return redirect(url_for('ogretmen_islem'))
            else:
                error = "Geçersiz kullanıcı adı veya şifre."
        finally:
            conn.close()

    return render_template('Giris/ogretmen_giris.html', error=error)

# Öğretmen Kayıt
@app.route('/Kayit/ogretmen_kayit', methods=['GET', 'POST'])
def ogretmen_kayit():
    if request.method == 'POST':
        ogretmenID = request.form['ogretmenID']
        sifre = request.form['sifre']
        email = request.form['email']

        try:
            conn = get_db_connection()
            ogretmen = Ogretmen(ogretmenID, sifre, email)
            ogretmen.kayit(conn)
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Bu Öğretmen ID zaten kayıtlı!", 400
        finally:
            conn.close()

    return render_template('Kayit/ogretmen_kayit.html')

# Öğretmen İşlem Sayfası
@app.route('/Islemler/ogretmen_islem', methods=['GET', 'POST'])
def ogretmen_islem():
    if 'ogretmenID' not in session:
        return redirect(url_for('ogretmen_giris'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ders programını veritabanından al
        cursor.execute("SELECT * FROM DersProgrami")
        ders_programi = cursor.fetchall()

        if request.method == 'POST':
            action = request.form.get('action')
            ders_id = request.form.get('dersID')
            gun = request.form.get('gun')
            saat = request.form.get('saat')
            ders_adi = request.form.get('ders_adi')

            if action == 'add':
                try:
                    cursor.execute("""
                        INSERT INTO DersProgrami (gun, saat, ders_adi)
                        VALUES (?, ?, ?)
                    """, (gun, saat, ders_adi))
                    conn.commit()
                except sqlite3.IntegrityError:
                    return "Ders eklenirken bir hata oluştu.", 400

            elif action == 'update' and ders_id:
                cursor.execute("""
                    UPDATE DersProgrami
                    SET gun = ?, saat = ?, ders_adi = ?
                    WHERE dersID = ?
                """, (gun, saat, ders_adi, ders_id))
                conn.commit()

            elif action == 'delete' and ders_id:
                cursor.execute("DELETE FROM DersProgrami WHERE dersID = ?", (ders_id,))
                conn.commit()

            return redirect(url_for('ogretmen_islem'))

        return render_template('Islemler/ogretmen_islem.html', ders_programi=ders_programi)
    except Exception as e:
        return f"Hata oluştu: {e}"
    finally:
        conn.close()

# Yönetici Kayıt
@app.route('/Kayit/yonetici_kayit', methods=['GET', 'POST'])
def yonetici_kayit():
    if request.method == 'POST':
        yoneticiID = request.form['yoneticiID']
        sifre = request.form['sifre']
        email = request.form['email']

        try:
            conn = get_db_connection()
            yonetici = Yonetici(yoneticiID, sifre, email)
            yonetici.kayit(conn)
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Bu yönetici ID zaten kayıtlı!", 400
        finally:
            conn.close()

    return render_template('Kayit/yonetici_kayit.html')


# Yönetici Giriş
@app.route('/Giris/yonetici_giris', methods=['GET', 'POST'])
def yonetici_giris():
    error = None
    if request.method == 'POST':
        yoneticiID = request.form['yoneticiID']
        sifre = request.form['sifre']

        try:
            conn = get_db_connection()
            yonetici = Yonetici.giris(conn, yoneticiID, sifre)

            if yonetici:
                session['yoneticiID'] = yoneticiID
                return redirect(url_for('yonetici_islem'))
            else:
                error = "Geçersiz kullanıcı adı veya şifre."
        finally:
            conn.close()

    return render_template('Giris/yonetici_giris.html', error=error)

# Yönetici İşlem Sayfası
@app.route('/Islemler/yonetici_islem', methods=['GET', 'POST'])
def yonetici_islem():
    if 'yoneticiID' not in session:
        return redirect(url_for('yonetici_giris'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        
        
        # Katılım durumu verilerini al
        cursor.execute(''' 
            SELECT 
                dp.gun,
                dp.saat,
                d.durak_adi,
                COUNT(CASE WHEN kd.katilim = 'katil' THEN 1 END) AS katilan_ogrenci
            FROM KatilimDurumu kd
            JOIN DersProgrami dp ON kd.dersID = dp.dersID
            JOIN Duraklar d ON kd.durakID = d.durakID
            GROUP BY dp.gun, dp.saat, d.durak_adi
            ORDER BY dp.gun, dp.saat, d.durak_adi;
        ''')
        durak_katilim = cursor.fetchall()

        # Mevcut rotalarda kullanılan durakları al
        cursor.execute('''
            SELECT gun, saat, durakID 
            FROM Rotalar
        ''')
        kullanilan_duraklar = cursor.fetchall()

        # Durakları filtrele: Kullanılmayan durakları göster
        uygun_duraklar = []
        for gun, saat, durak_adi, katilan_ogrenci in durak_katilim:
            cursor.execute("SELECT durakID FROM Duraklar WHERE durak_adi = ?", (durak_adi,))
            durak_id = cursor.fetchone()
            if durak_id and (gun, saat, durak_id[0]) not in kullanilan_duraklar:
                uygun_duraklar.append((gun, saat, durak_adi, katilan_ogrenci))

        # Şoförler listesi
        cursor.execute('SELECT * FROM Soforler')
        soforler = cursor.fetchall()

        # Rotalar
        cursor.execute('SELECT * FROM Rotalar')
        rotalar = cursor.fetchall()

        if request.method == 'POST':
            action = request.form.get('action')
            sofor_id = request.form.get('soforID')
            selected_duraklar = request.form.getlist('selected_duraklar')  # Liste olarak al
            saat= request.form.get('yeniSaat')
            rotaID= request.form.get('rotaID')
            
            print('rota verileri ', action, sofor_id, selected_duraklar, saat)

            if action == 'RotaOlustur' and selected_duraklar:
                try:
                    for durak in selected_duraklar:
                        gun, durak_adi = durak.split(',')

                        # Durak ID'sini al
                        cursor.execute("SELECT durakID FROM Duraklar WHERE durak_adi = ?", (durak_adi,))
                        durakID = cursor.fetchone()

                        if durakID:
                            durakID = durakID[0]

                            # Mevcut rota kontrolü (gün, saat, şoför eşleşiyor mu?)
                            cursor.execute("""
                                SELECT rotaID, durakID FROM Rotalar 
                                WHERE gun = ? AND saat = ? AND soforID = ?
                            """, (gun, saat, sofor_id))
                            existing_rota = cursor.fetchone()

                            if existing_rota:
                                # Var olan rota ile durakları birleştir
                                rotaID, existing_durakID = existing_rota
                                updated_durakID = f"{existing_durakID},{durakID}" if existing_durakID else str(durakID)

                                # Mevcut rotayı güncelle
                                cursor.execute("""
                                    UPDATE Rotalar
                                    SET durakID = ?
                                    WHERE rotaID = ?
                                """, (updated_durakID, rotaID))
                            else:
                                # Yeni bir rota ekle
                                cursor.execute("""
                                    INSERT INTO Rotalar (gun, saat, soforID, durakID)
                                    VALUES (?, ?, ?, ?)
                                """, (gun, saat, sofor_id, durakID))
                        else:
                            return f"Durak bulunamadı: {durak_adi}", 400                    

                    conn.commit()
                    flash("Rota başarıyla oluşturuldu.")
                except Exception as e:
                    return f"Rota eklenirken bir hata oluştu: {e}", 500
                
            elif action== 'rota_sil':
                cursor.execute("DELETE FROM Rotalar WHERE rotaID = ?", (rotaID,))
                conn.commit()
            
            elif action == 'rota_guncelle':

                return redirect(url_for('rota_guncelle' , rotaID=rotaID))



            return redirect(url_for('yonetici_islem'))
            


        return render_template(
            'Islemler/yonetici_islem.html', 
            katilim=uygun_duraklar, 
            rotalar=rotalar,
            soforler=soforler

        )

    except Exception as e:
        return f"Hata oluştus: {e}"
    finally:
        conn.close()

@app.route('/Islemler/rota_guncelle/<int:rotaID>', methods=['GET', 'POST'])
def rota_guncelle(rotaID):
    if 'yoneticiID' not in session:
        return redirect(url_for('yonetici_giris'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Duraklar")
        duraklar = cursor.fetchall()


        if request.method == 'POST':
            # Formdan gelen güncel bilgiler
            yeni_saat = request.form['yeniSaat']
            yeni_soforID = request.form['yeniSoforID']
            selected_duraklar = request.form.getlist('selected_duraklar')


            # Rotayı güncelle
            cursor.execute("""
                UPDATE Rotalar
                SET saat = ?, soforID = ?, durakID = ?
                WHERE rotaID = ?
            """, (yeni_saat, yeni_soforID, rotaID, selected_duraklar))
            conn.commit()

            flash("Rota başarıyla güncellendi.")
            return redirect(url_for('yonetici_islem'))

        # Mevcut rota bilgilerini al
        cursor.execute("""
            SELECT gun, saat, soforID, durakID
            FROM Rotalar
            WHERE rotaID = ?
        """, (rotaID,))
        rota = cursor.fetchone()

        # Şoför listesi
        cursor.execute("SELECT soforID FROM Soforler")
        soforler = cursor.fetchall()

        return render_template('Islemler/rota_guncelle.html', rota=rota, soforler=soforler, duraklar=duraklar)
    except Exception as e:
        return f"Hata oluştu: {e}"
    finally:
        conn.close()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Saat ve durak bazında katılım durumunu al
        cursor.execute('''
            SELECT
                dp.gun,
                dp.saat,
                d.durak_adi,
                COUNT(CASE WHEN kd.katilim = 'katil' THEN 1 END ) AS katilan_ogrenci
            FROM KatilimDurumu kd
            JOIN DersProgrami dp ON kd.dersID = dp.dersID
            JOIN Duraklar d ON kd.durakID = d.durakID
            GROUP BY dp.saat, d.durak_adi
            ORDER BY dp.saat, d.durak_adi;
        ''')
        durak_katilim = cursor.fetchall()

        otobus_kapasitesi = 20
        otobus_sayilari = []
        for gun, saat, durak, katilan_ogrenci in durak_katilim:
            otobus_sayisi = (katilan_ogrenci + otobus_kapasitesi - 1) // otobus_kapasitesi
            bos_otobus_sayisi = max(0, otobus_sayisi - (katilan_ogrenci // otobus_kapasitesi))
            otobus_sayilari.append((gun, saat, durak, katilan_ogrenci, otobus_sayisi, bos_otobus_sayisi))

        # Şoförleri ve durakları al
        cursor.execute("SELECT soforID FROM Soforler")
        soforler = cursor.fetchall()

        cursor.execute("SELECT durakID, durak_adi FROM Duraklar")
        duraklar = cursor.fetchall()

        if request.method == 'POST':
            gun = request.form.get('gun')
            saat = request.form.get('saat')
            sofor_id = request.form.get('soforID')
            durak_id = request.form.get('durakID')

            print("Form verileri: ", gun, saat, sofor_id, durak_id)

            # Seçilen verilerle yeni bir rota oluştur
            if gun and saat and sofor_id and durak_id:
                cursor.execute('''
                    INSERT INTO Rotalar (gun, saat, soforID, durakID)
                    VALUES (?, ?, ?, ?)
                ''', (gun, saat, sofor_id, durak_id))
                conn.commit()
                flash("Rota başarıyla oluşturuldu!")
                return redirect(url_for('yonetici_islem'))

        return render_template('Islemler/yonetici_islem.html', 
                               otobus_sayilari=otobus_sayilari, 
                               soforler=soforler, 
                               duraklar=duraklar)

    except Exception as e:
        return f"Hata oluştu: {e}"
    finally:
        conn.close()


# Şoför Giriş
@app.route('/Giris/sofor_giris', methods=['GET', 'POST'])
def sofor_giris():
    error = None
    if request.method == 'POST':
        soforID = request.form['soforID']
        sifre = request.form['sifre']

        try:
            conn = get_db_connection()
            sofor = Sofor.giris(conn, soforID, sifre)

            if sofor:
                session['soforID'] = soforID
                return redirect(url_for('sofor_islem'))
            else:
                error = "Geçersiz kullanıcı adı veya şifre."
        finally:
            conn.close()

    return render_template('Giris/sofor_giris.html', error=error)

# Şoför Kayıt
@app.route('/Kayit/sofor_kayit', methods=['GET', 'POST'])
def sofor_kayit():
    if request.method == 'POST':
        soforID = request.form['soforID']
        sifre = request.form['sifre']
        email = request.form['email']

        try:
            conn = get_db_connection()
            sofor = Sofor(soforID, sifre, email)
            sofor.kayit(conn)
            flash("Kayıt başarılı")
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Bu Şoför ID zaten kayıtlı!", 400
        finally:
            conn.close()

    return render_template('Kayit/sofor_kayit.html')

@app.route('/Islemler/sofor_islem', methods=['GET', 'POST'])
def sofor_islem():
    if 'soforID' not in session:
        return redirect(url_for('sofor_giris'))  # Şoför giriş yapmamışsa yönlendirme

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Oturumdaki şoför ID'sini al
        sofor_id = session['soforID']

        # Şoförün rotalarını al
        cursor.execute('''
            SELECT r.rotaID, r.gun, r.saat, d.durak_adi 
            FROM Rotalar r
            JOIN Duraklar d ON r.durakID = d.durakID
            WHERE r.soforID = ?
        ''', (sofor_id,))
        rotalar = cursor.fetchall()

        return render_template('Islemler/sofor_islem.html', rotalar=rotalar)
    except Exception as e:
        return f"Hata oluştu: {e}"
    finally:
        conn.close()




# Çıkış Yap
@app.route('/Giris/cikis')
def cikis():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
