from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
from functools import wraps # wraps decorator'u için eklendi
from sqlalchemy.orm import aliased # aliased fonksiyonunu import et

# --- UYGULAMA KURULUMU ---
app = Flask(__name__)
# Session (oturum) ve veritabanı ayarları
app.config['SECRET_KEY'] = 'cok-gizli-bir-anahtar-bunu-degistirin'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'hastane.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
KONTENJAN = 10 # Günlük doktor kontenjanı


# --- VERİTABANI MODELLERİ (SQLAlchemy) ---
# Kullanıcı rolleri için ortak bir temel model
class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    sifre = db.Column(db.String(200), nullable=False)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    rol = db.Column(db.String(20), nullable=False) # 'hasta', 'doktor', 'sekreter'

    __mapper_args__ = {
        'polymorphic_identity': 'kullanici',
        'polymorphic_on': rol
    }

class Hasta(Kullanici):
    def __init__(self, **kwargs):
        super(Hasta, self).__init__(**kwargs)
        self.rol = 'hasta'

    __mapper_args__ = {'polymorphic_identity': 'hasta'}
    randevular = db.relationship(
        'Randevu', 
        foreign_keys='Randevu.hasta_id', 
        backref='hasta', 
        lazy=True
    )

class Doktor(Kullanici):
    def __init__(self, **kwargs):
        super(Doktor, self).__init__(**kwargs)
        self.rol = 'doktor'

    __mapper_args__ = {'polymorphic_identity': 'doktor'}
    brans_id = db.Column(db.Integer, db.ForeignKey('brans.id'), nullable=True)
    randevular = db.relationship(
        'Randevu', 
        foreign_keys='Randevu.doktor_id', 
        backref='doktor', 
        lazy=True
    )

class Sekreter(Kullanici):
    def __init__(self, **kwargs):
        super(Sekreter, self).__init__(**kwargs)
        self.rol = 'sekreter'

    __mapper_args__ = {'polymorphic_identity': 'sekreter'}

class Brans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), unique=True, nullable=False)
    emoji = db.Column(db.String(10), nullable=True) # Emoji için yeni alan
    doktorlar = db.relationship('Doktor', backref='brans', lazy=True)

class Randevu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hasta_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    doktor_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    tarih = db.Column(db.DateTime, nullable=False)
    sikayet = db.Column(db.Text, nullable=True)
    durum = db.Column(db.String(50), default='Bekleniyor') # Bekleniyor, Tamamlandı, İptal

class Duyuru(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    icerik = db.Column(db.Text, nullable=False)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    olusturan_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    olusturan = db.relationship('Kullanici', backref='duyurular')


# --- SAYFA YÖNLENDİRMELERİ (Routes) ---

# Rol tabanlı erişim kontrolü için yardımcı fonksiyon
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
                return redirect(url_for('index')) # Artık var olmayan 'login' yerine 'index'e (ana sayfa) yönlendir.
            if role and session['user_rol'] != role:
                flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
                return redirect(url_for('index')) # Yetkisiz kullanıcıyı ana sayfaya veya kendi paneline yönlendir
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('index'))

@app.route('/kayit_ol', methods=['GET', 'POST'])
def kayit_ol():
    if request.method == 'POST':
        ad = request.form['ad']
        soyad = request.form['soyad']
        email = request.form['email']
        sifre = request.form['sifre']

        if Kullanici.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor.', 'danger')
            return redirect(url_for('kayit_ol'))

        hashli_sifre = generate_password_hash(sifre, method='pbkdf2:sha256')
        yeni_hasta = Hasta(ad=ad, soyad=soyad, email=email, sifre=hashli_sifre, rol='hasta')
        
        db.session.add(yeni_hasta)
        db.session.commit()

        flash('Kaydınız başarıyla oluşturuldu! Lütfen giriş yapın.', 'success')
        return redirect(url_for('hasta_login')) # Hasta kaydı sonrası hasta girişine yönlendir

    return render_template('kayit_ol.html')

# --- Role Özel Giriş Rotaları ---
@app.route('/hasta_login', methods=['GET', 'POST'])
def hasta_login():
    if request.method == 'POST':
        email = request.form['email']
        sifre = request.form['sifre']
        kullanici = Kullanici.query.filter_by(email=email, rol='hasta').first()

        if kullanici and check_password_hash(kullanici.sifre, sifre):
            session['user_id'] = kullanici.id
            session['user_rol'] = kullanici.rol
            session['user_ad'] = kullanici.ad
            flash('Hasta girişi başarılı!', 'success')
            return redirect(url_for('hasta_paneli'))
        else:
            flash('E-posta veya şifre hatalı, veya bu hesap bir hasta hesabı değil.', 'danger')
            return redirect(url_for('hasta_login'))
    return render_template('hasta_login.html')

@app.route('/doktor_login', methods=['GET', 'POST'])
def doktor_login():
    if request.method == 'POST':
        email = request.form['email']
        sifre = request.form['sifre']
        kullanici = Kullanici.query.filter_by(email=email, rol='doktor').first()

        if kullanici and check_password_hash(kullanici.sifre, sifre):
            session['user_id'] = kullanici.id
            session['user_rol'] = kullanici.rol
            session['user_ad'] = kullanici.ad
            flash('Doktor girişi başarılı!', 'success')
            return redirect(url_for('doktor_paneli'))
        else:
            flash('E-posta veya şifre hatalı, veya bu hesap bir doktor hesabı değil.', 'danger')
            return redirect(url_for('doktor_login'))
    return render_template('doktor_login.html')

@app.route('/sekreter_login', methods=['GET', 'POST'])
def sekreter_login():
    if request.method == 'POST':
        email = request.form['email']
        sifre = request.form['sifre']
        kullanici = Kullanici.query.filter_by(email=email, rol='sekreter').first()

        if kullanici and check_password_hash(kullanici.sifre, sifre):
            session['user_id'] = kullanici.id
            session['user_rol'] = kullanici.rol
            session['user_ad'] = kullanici.ad
            flash('Sekreter girişi başarılı!', 'success')
            return redirect(url_for('sekreter_paneli'))
        else:
            flash('E-posta veya şifre hatalı, veya bu hesap bir sekreter hesabı değil.', 'danger')
            return redirect(url_for('sekreter_login'))
    return render_template('sekreter_login.html')

# --- Panel Sayfaları (Giriş yapmış kullanıcılar için) ---

@app.route('/hasta_paneli')
@login_required(role='hasta')
def hasta_paneli():
    hasta_id = session['user_id']
    # Hastanın randevularını çek (gelecek ve geçmiş)
    randevular = Randevu.query.filter_by(hasta_id=hasta_id).order_by(Randevu.tarih.desc()).all()
    return render_template('hasta_paneli.html', randevular=randevular, now=datetime.now()) # now() değerini şablona gönder

@app.route('/profil', methods=['GET', 'POST'])
@login_required()
def profil_duzenle():
    kullanici = Kullanici.query.get_or_404(session['user_id'])
    if request.method == 'POST':
        # Bilgi Güncelleme
        kullanici.ad = request.form.get('ad')
        kullanici.soyad = request.form.get('soyad')
        
        # Şifre Değiştirme
        mevcut_sifre = request.form.get('mevcut_sifre')
        yeni_sifre = request.form.get('yeni_sifre')
        yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar')

        if mevcut_sifre and yeni_sifre and yeni_sifre_tekrar:
            if not check_password_hash(kullanici.sifre, mevcut_sifre):
                flash('Mevcut şifreniz hatalı!', 'danger')
                return render_template('profil_duzenle.html', kullanici=kullanici)
            
            if yeni_sifre != yeni_sifre_tekrar:
                flash('Yeni şifreler uyuşmuyor!', 'danger')
                return render_template('profil_duzenle.html', kullanici=kullanici)
            
            kullanici.sifre = generate_password_hash(yeni_sifre, method='pbkdf2:sha256')
            flash('Şifreniz başarıyla güncellendi.', 'success')

        db.session.commit()
        # Session'daki adı güncelle
        session['user_ad'] = kullanici.ad
        flash('Profil bilgileriniz başarıyla güncellendi.', 'success')
        return redirect(url_for('profil_duzenle'))

    return render_template('profil_duzenle.html', kullanici=kullanici)


@app.route('/hasta_randevu_iptal/<int:randevu_id>')
@login_required(role='hasta')
def hasta_randevu_iptal(randevu_id):
    randevu = Randevu.query.get_or_404(randevu_id)
    if randevu.hasta_id != session['user_id']:
        flash('Bu randevuyu iptal etme yetkiniz yok.', 'danger')
        return redirect(url_for('hasta_paneli'))
    
    if randevu.tarih < datetime.now():
        flash('Geçmiş randevular iptal edilemez.', 'danger')
    else:
        randevu.durum = 'İptal Edildi'
        db.session.commit()
        flash('Randevunuz başarıyla iptal edildi.', 'success')
    return redirect(url_for('hasta_paneli'))

@app.route('/hasta/randevu_detay/<int:randevu_id>')
@login_required(role='hasta')
def hasta_randevu_detay(randevu_id):
    randevu = Randevu.query.get_or_404(randevu_id)
    # Hasta sadece kendi randevu detayını görebilir
    if randevu.hasta_id != session['user_id']:
        flash('Bu randevu detayını görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('hasta_paneli'))
    
    return render_template('hasta_randevu_detay.html', randevu=randevu)

# --- MHRS Benzeri Randevu Akışı ---

@app.route('/hasta_randevu_al')
@login_required(role='hasta')
def hasta_randevu_brans_sec():
    branslar = Brans.query.order_by(Brans.ad).all()
    return render_template('hasta_randevu_brans_sec.html', branslar=branslar)

@app.route('/randevu_al/doktor_sec/<int:brans_id>', methods=['GET', 'POST'])
@login_required(role='hasta')
def hasta_randevu_doktor_sec(brans_id):
    brans = Brans.query.get_or_404(brans_id)
    doktorlar = Doktor.query.filter_by(brans_id=brans_id).order_by(Doktor.soyad).all()
    
    if request.method == 'POST':
        doktor_id = request.form.get('doktor_id')
        tarih_str = request.form.get('tarih')
        saat_str = request.form.get('saat')
        sikayet = request.form.get('sikayet', '')

        if not all([doktor_id, tarih_str, saat_str]):
            flash('Lütfen doktor, tarih ve saat seçimi yapınız.', 'danger')
            return redirect(url_for('hasta_randevu_doktor_sec', brans_id=brans_id))

        try:
            randevu_tarihi = datetime.strptime(f"{tarih_str} {saat_str}", '%Y-%m-%d %H:%M')

            # KONTENJAN VE SAAT KONTROLÜ
            # Seçilen saatte zaten bir randevu var mı?
            is_slot_taken = Randevu.query.filter_by(doktor_id=doktor_id, tarih=randevu_tarihi).first()
            if is_slot_taken:
                flash('Seçtiğiniz saat dilimi dolmuştur. Lütfen başka bir saat seçin.', 'danger')
                return redirect(url_for('hasta_randevu_doktor_sec', brans_id=brans_id))

            yeni_randevu = Randevu(
                hasta_id=session['user_id'],
                doktor_id=doktor_id,
                tarih=randevu_tarihi,
                sikayet=sikayet
            )
            db.session.add(yeni_randevu)
            db.session.commit()
            flash(f'Randevunuz {tarih_str} {saat_str} için başarıyla oluşturuldu!', 'success')
            return redirect(url_for('hasta_paneli'))

        except Exception as e:
            flash(f'Randevu oluşturulurken bir hata oluştu: {e}', 'danger')
            return redirect(url_for('hasta_randevu_doktor_sec', brans_id=brans_id))

    return render_template('hasta_randevu_doktor_sec.html', brans=brans, doktorlar=doktorlar, datetime=datetime)

# --- API Rotaları (Dinamik içerik için) ---

@app.route('/api/available_slots/<int:doktor_id>/<string:tarih>')
@login_required() # Sadece giriş yapmış kullanıcılar erişebilir
def available_slots(doktor_id, tarih):
    try:
        secilen_tarih = datetime.strptime(tarih, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Geçersiz tarih formatı'}), 400

    # Çalışma saatleri ve randevu aralığı
    calisma_baslangic = 9
    calisma_bitis = 17
    randevu_araligi_dk = 10 # Her randevu 10 dakika

    # O günkü dolu saatleri veritabanından çek
    start_of_day = datetime.combine(secilen_tarih, datetime.min.time())
    end_of_day = datetime.combine(secilen_tarih, datetime.max.time())
    dolu_randevular = Randevu.query.filter(
        Randevu.doktor_id == doktor_id,
        Randevu.tarih.between(start_of_day, end_of_day),
        or_(Randevu.durum == 'Bekleniyor', Randevu.durum == 'Tamamlandı') # İptal edilenler dolu sayılmaz
    ).all()
    dolu_saatler = {randevu.tarih.strftime('%H:%M') for randevu in dolu_randevular}

    # Müsait saatleri oluştur
    musait_saatler = []
    current_time = datetime.now().time()
    today = datetime.now().date()

    for saat in range(calisma_baslangic, calisma_bitis):
        for dakika in range(0, 60, randevu_araligi_dk):
            slot_time_str = f"{saat:02d}:{dakika:02d}"
            slot_time = datetime.strptime(slot_time_str, '%H:%M').time()
            
            # Geçmiş saatleri ve dolu saatleri atla
            if secilen_tarih == today and slot_time <= current_time:
                continue
            if slot_time_str not in dolu_saatler:
                musait_saatler.append(slot_time_str)
    
    # Günlük kontenjan kontrolü
    if len(dolu_randevular) >= KONTENJAN:
        return jsonify({'kontenjan_dolu': True, 'slots': []})

    return jsonify({'kontenjan_dolu': False, 'slots': musait_saatler})

@app.route('/doktor_paneli')
@login_required(role='doktor')
def doktor_paneli():
    doktor_id = session['user_id']
    # Doktorun yaklaşan randevularını çek
    randevular = Randevu.query.filter_by(doktor_id=doktor_id).filter(Randevu.tarih >= datetime.now()).order_by(Randevu.tarih.asc()).all()
    # Tüm duyuruları çek
    duyurular = Duyuru.query.order_by(Duyuru.olusturma_tarihi.desc()).all()
    return render_template('doktor_paneli.html', randevular=randevular, duyurular=duyurular)

@app.route('/doktor/randevu_tamamla/<int:randevu_id>', methods=['POST'])
@login_required(role='doktor')
def doktor_randevu_tamamla(randevu_id):
    randevu = Randevu.query.get_or_404(randevu_id)
    # Sadece kendi randevusunu tamamlayabilsin
    if randevu.doktor_id != session['user_id']:
        flash('Bu işlem için yetkiniz yok.', 'danger')
        return redirect(url_for('doktor_paneli'))
    
    randevu.durum = 'Tamamlandı'
    db.session.commit()
    flash('Randevu "Tamamlandı" olarak işaretlendi.', 'success')
    return redirect(url_for('doktor_paneli'))

@app.route('/doktor/randevu_not_ekle/<int:randevu_id>', methods=['GET', 'POST'])
@login_required(role='doktor')
def doktor_randevu_not_ekle(randevu_id):
    randevu = Randevu.query.get_or_404(randevu_id)
    # Sadece kendi randevusuna not ekleyebilsin
    if randevu.doktor_id != session['user_id']:
        flash('Bu işlem için yetkiniz yok.', 'danger')
        return redirect(url_for('doktor_paneli'))

    if request.method == 'POST':
        not_icerik = request.form.get('doktor_notu')
        randevu.doktor_notu = not_icerik
        db.session.commit()
        flash('Randevu notu başarıyla kaydedildi.', 'success')
        return redirect(url_for('doktor_paneli'))

    # Not ekleme/düzenleme sayfası için yeni bir template oluşturalım
    return render_template('doktor_randevu_not_ekle.html', randevu=randevu)

@app.route('/doktor/hasta_gecmisi/<int:hasta_id>')
@login_required(role='doktor')
def doktor_hasta_gecmisi(hasta_id):
    hasta = Hasta.query.get_or_404(hasta_id)
    # Hastanın tüm randevularını, en yeniden eskiye doğru sırala
    randevular = Randevu.query.filter_by(hasta_id=hasta.id).order_by(Randevu.tarih.desc()).all()

    return render_template('doktor_hasta_gecmisi.html', hasta=hasta, randevular=randevular)


@app.route('/sekreter_paneli')
@login_required(role='sekreter')
def sekreter_paneli():
    # İstatistikler için hesaplamalar
    toplam_hasta = Hasta.query.count()
    toplam_doktor = Doktor.query.count()
    onay_bekleyen_randevu = Randevu.query.filter_by(durum='Bekleniyor').count()
    
    today_start = datetime.combine(datetime.today(), datetime.min.time())
    today_end = datetime.combine(datetime.today(), datetime.max.time())
    bugunku_randevu_sayisi = Randevu.query.filter(Randevu.tarih.between(today_start, today_end)).count()

    return render_template('sekreter_paneli.html', toplam_hasta=toplam_hasta, toplam_doktor=toplam_doktor, 
                           onay_bekleyen_randevu=onay_bekleyen_randevu, bugunku_randevu_sayisi=bugunku_randevu_sayisi)

@app.route('/sekreter_doktor_ekle', methods=['GET', 'POST'])
@login_required(role='sekreter')
def sekreter_doktor_ekle():
    branslar = Brans.query.all() # Doktor eklerken branş seçimi için
    if request.method == 'POST':
        ad = request.form['ad']
        soyad = request.form['soyad']
        email = request.form['email']
        sifre = request.form['sifre']
        brans_id = request.form['brans_id']

        if Kullanici.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor.', 'danger')
            return redirect(url_for('sekreter_doktor_ekle'))

        hashli_sifre = generate_password_hash(sifre, method='pbkdf2:sha256')
        yeni_doktor = Doktor(ad=ad, soyad=soyad, email=email, sifre=hashli_sifre, brans_id=brans_id)
        
        db.session.add(yeni_doktor)
        db.session.commit()
        flash(f'Doktor {ad} {soyad} başarıyla eklendi!', 'success')
        return redirect(url_for('sekreter_paneli'))
    return render_template('sekreter_doktor_ekle.html', branslar=branslar)

@app.route('/sekreter_brans_yonetimi', methods=['GET', 'POST'])
@login_required(role='sekreter')
def sekreter_brans_yonetimi():
    if request.method == 'POST':
        brans_adi = request.form['brans_adi'].strip()
        if not brans_adi:
            flash('Branş adı boş bırakılamaz.', 'danger')
        elif Brans.query.filter_by(ad=brans_adi).first():
            flash('Bu branş zaten mevcut.', 'danger')
        else:
            yeni_brans = Brans(ad=brans_adi)
            db.session.add(yeni_brans)
            db.session.commit()
            flash(f'{brans_adi} branşı başarıyla eklendi!', 'success')
        return redirect(url_for('sekreter_brans_yonetimi'))
    
    branslar = Brans.query.all()
    return render_template('sekreter_brans_yonetimi.html', branslar=branslar)

@app.route('/sekreter_duyuru_olustur', methods=['GET', 'POST'])
@login_required(role='sekreter')
def sekreter_duyuru_olustur():
    if request.method == 'POST':
        baslik = request.form['baslik']
        icerik = request.form['icerik']
        
        yeni_duyuru = Duyuru(
            baslik=baslik,
            icerik=icerik,
            olusturan_id=session['user_id'] # Duyuruyu oluşturan sekreterin ID'si
        )
        db.session.add(yeni_duyuru)
        db.session.commit()
        flash('Duyuru başarıyla oluşturuldu!', 'success')
        return redirect(url_for('sekreter_paneli'))
    return render_template('sekreter_duyuru_olustur.html')

@app.route('/sekreter_randevu_yonetimi')
@login_required(role='sekreter')
def sekreter_randevu_yonetimi():
    # Filtreleme için formdan gelen verileri al (GET request)
    q_hasta = request.args.get('q_hasta', '')
    q_doktor_id = request.args.get('q_doktor_id', '')
    q_durum = request.args.get('q_durum', '')
    q_tarih_bas = request.args.get('q_tarih_bas', '')
    q_tarih_bit = request.args.get('q_tarih_bit', '')

    # Belirsizliği (ambiguity) çözmek için aliased kullanımı
    doktor_alias = aliased(Doktor)
    hasta_alias = aliased(Hasta)

    query = Randevu.query.join(doktor_alias, Randevu.doktor_id == doktor_alias.id)\
                         .join(hasta_alias, Randevu.hasta_id == hasta_alias.id)

    if q_hasta:
        search = f"%{q_hasta}%"
        query = query.filter(or_(hasta_alias.ad.ilike(search), hasta_alias.soyad.ilike(search)))
    if q_doktor_id:
        query = query.filter(doktor_alias.id == q_doktor_id)
    if q_durum:
        query = query.filter(Randevu.durum == q_durum)
    if q_tarih_bas:
        tarih_bas = datetime.strptime(q_tarih_bas, '%Y-%m-%d')
        query = query.filter(Randevu.tarih >= tarih_bas)
    if q_tarih_bit:
        tarih_bit = datetime.strptime(q_tarih_bit, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(Randevu.tarih <= tarih_bit)

    randevular = query.order_by(Randevu.tarih.desc()).all()
    
    # Filtre formları için doktor listesi
    doktorlar = Doktor.query.order_by(Doktor.ad).all()

    return render_template('sekreter_randevu_yonetimi.html', randevular=randevular, now=datetime.now(), 
                           doktorlar=doktorlar, query_params=request.args)

@app.route('/sekreter_randevu_olustur', methods=['GET', 'POST'])
@login_required(role='sekreter')
def sekreter_randevu_olustur():
    doktorlar = Doktor.query.join(Brans).add_columns(Doktor.id, Doktor.ad, Doktor.soyad, Brans.ad.label('brans_ad')).all()
    hastalar = Hasta.query.all()

    if request.method == 'POST':
        hasta_id = request.form['hasta_id']
        doktor_id = request.form['doktor_id']
        tarih_str = request.form['tarih']
        saat_str = request.form['saat']
        sikayet = request.form['sikayet']
        durum = request.form['durum']

        try:
            randevu_tarihi = datetime.strptime(f"{tarih_str} {saat_str}", '%Y-%m-%d %H:%M')

            # KONTENJAN KONTROLÜ
            start_of_day = datetime.combine(randevu_tarihi.date(), datetime.min.time())
            end_of_day = datetime.combine(randevu_tarihi.date(), datetime.max.time())
            mevcut_randevu_sayisi = Randevu.query.filter(
                Randevu.doktor_id == doktor_id,
                Randevu.tarih.between(start_of_day, end_of_day)
            ).count()
            if mevcut_randevu_sayisi >= KONTENJAN:
                flash(f'Seçtiğiniz doktorun {tarih_str} tarihi için kontenjanı dolmuştur. Lütfen başka bir tarih seçin.', 'danger')
                return redirect(url_for('sekreter_randevu_olustur'))
            
            yeni_randevu = Randevu(
                hasta_id=hasta_id,
                doktor_id=doktor_id,
                tarih=randevu_tarihi,
                sikayet=sikayet,
                durum=durum
            )
            db.session.add(yeni_randevu)
            db.session.commit()
            flash('Randevu başarıyla oluşturuldu.', 'success')
            return redirect(url_for('sekreter_randevu_yonetimi'))
        except ValueError:
            flash('Geçersiz tarih veya saat formatı.', 'danger')
        except Exception as e:
            flash(f'Randevu oluşturulurken bir hata oluştu: {e}', 'danger')

    return render_template('sekreter_randevu_olustur.html', doktorlar=doktorlar, hastalar=hastalar, datetime=datetime)

@app.route('/sekreter_randevu_duzenle/<int:randevu_id>', methods=['GET', 'POST'])
@login_required(role='sekreter')
def sekreter_randevu_duzenle(randevu_id):
    randevu = Randevu.query.get_or_404(randevu_id)
    doktorlar = Doktor.query.join(Brans).add_columns(Doktor.id, Doktor.ad, Doktor.soyad, Brans.ad.label('brans_ad')).all()
    hastalar = Hasta.query.all()
    
    if request.method == 'POST':
        randevu.hasta_id = request.form['hasta_id']
        randevu.doktor_id = request.form['doktor_id']
        tarih_str = request.form['tarih']
        saat_str = request.form['saat']
        randevu.sikayet = request.form['sikayet']
        randevu.durum = request.form['durum']

        try:
            randevu.tarih = datetime.strptime(f"{tarih_str} {saat_str}", '%Y-%m-%d %H:%M')
            db.session.commit()
            flash('Randevu başarıyla güncellendi.', 'success')
            return redirect(url_for('sekreter_randevu_yonetimi'))
        except ValueError:
            flash('Geçersiz tarih veya saat formatı.', 'danger')
        except Exception as e:
            flash(f'Randevu güncellenirken bir hata oluştu: {e}', 'danger')

    return render_template(
        'sekreter_randevu_duzenle.html',
        randevu=randevu,
        doktorlar=doktorlar,
        hastalar=hastalar,
        datetime=datetime
    )

@app.route('/sekreter_randevu_sil/<int:randevu_id>', methods=['POST'])
@login_required(role='sekreter')
def sekreter_randevu_sil(randevu_id):
    randevu = Randevu.query.get_or_404(randevu_id)
    try:
        db.session.delete(randevu)
        db.session.commit()
        flash('Randevu başarıyla silindi.', 'success')
    except Exception as e:
        flash(f'Randevu silinirken bir hata oluştu: {e}', 'danger')
    return redirect(url_for('sekreter_randevu_yonetimi'))

@app.route('/sekreter_randevu_onayla/<int:randevu_id>', methods=['POST'])
@login_required(role='sekreter')
def sekreter_randevu_onayla(randevu_id):
    randevu = Randevu.query.get_or_404(randevu_id)
    if randevu.durum == 'Bekleniyor':
        try:
            randevu.durum = 'Onaylandı'
            db.session.commit()
            flash(f'Randevu (ID: {randevu.id}) başarıyla onaylandı.', 'success')
        except Exception as e:
            flash(f'Randevu onaylanırken bir hata oluştu: {e}', 'danger')
    else:
        flash(f'Randevu (ID: {randevu.id}) zaten "{randevu.durum}" durumunda, onaylanamaz.', 'warning')
    return redirect(url_for('sekreter_randevu_yonetimi'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Veritabanı ve tabloları oluşturur (eğer yoksa)
        
        # Başlangıç verileri ekle (sadece veritabanı boşsa)
        if not Brans.query.first():
            db.session.add(Brans(ad='Genel Cerrahi', emoji='⚕️'))
            db.session.add(Brans(ad='Kardiyoloji', emoji='❤️'))
            db.session.add(Brans(ad='Dahiliye', emoji='🩺'))
            db.session.add(Brans(ad='Pediatri', emoji='👶'))
            db.session.add(Brans(ad='Nöroloji', emoji='🧠'))
            db.session.add(Brans(ad='Ortopedi', emoji='🦴'))
            db.session.add(Brans(ad='Göz Hastalıkları', emoji='👁️'))
            db.session.add(Brans(ad='KBB', emoji='👂'))
            db.session.add(Brans(ad='Dermatoloji', emoji='🧴'))
            db.session.add(Brans(ad='Psikiyatri', emoji='🧘'))
            db.session.add(Brans(ad='Üroloji', emoji='💧'))
            db.session.add(Brans(ad='Fizik Tedavi', emoji='💪'))
            db.session.commit()
            print("Başlangıç branşları eklendi.")
        if not Sekreter.query.filter_by(email='sekreter@hastane.com').first():
            hashli_sifre = generate_password_hash('sekreter123', method='pbkdf2:sha256')
            default_sekreter = Sekreter(ad='Ayşe', soyad='Yılmaz', email='sekreter@hastane.com', sifre=hashli_sifre)
            db.session.add(default_sekreter)
            db.session.commit()
            print("Varsayılan sekreter eklendi: sekreter@hastane.com / sekreter123")
            
        if not Hasta.query.filter_by(email='hasta@hastane.com').first():
            hashli_sifre = generate_password_hash('hasta123', method='pbkdf2:sha256')
            default_hasta = Hasta(ad='Deniz', soyad='Can', email='hasta@hastane.com', sifre=hashli_sifre)
            db.session.add(default_hasta)
            db.session.commit()
            print("Varsayılan hasta eklendi: hasta@hastane.com / hasta123")

        if not Doktor.query.first():
            doktorlar_data = [
                {'ad': 'Mehmet', 'soyad': 'Demir', 'email': 'mehmet.demir@hastane.com', 'brans': 'Genel Cerrahi'},
                {'ad': 'Zeynep', 'soyad': 'Kaya', 'email': 'zeynep.kaya@hastane.com', 'brans': 'Kardiyoloji'},
                {'ad': 'Ali', 'soyad': 'Vural', 'email': 'ali.vural@hastane.com', 'brans': 'Pediatri'},
                {'ad': 'Fatma', 'soyad': 'Çelik', 'email': 'fatma.celik@hastane.com', 'brans': 'Dahiliye'},
                {'ad': 'Hasan', 'soyad': 'Yıldız', 'email': 'hasan.yildiz@hastane.com', 'brans': 'Nöroloji'},
                {'ad': 'Elif', 'soyad': 'Öztürk', 'email': 'elif.ozturk@hastane.com', 'brans': 'Göz Hastalıkları'},
                {'ad': 'Murat', 'soyad': 'Aydın', 'email': 'murat.aydin@hastane.com', 'brans': 'Kardiyoloji'},
            ]
            
            for d in doktorlar_data:
                brans = Brans.query.filter_by(ad=d['brans']).first()
                if brans:
                    hashli_sifre = generate_password_hash('doktor123', method='pbkdf2:sha256')
                    yeni_doktor = Doktor(
                        ad=d['ad'], soyad=d['soyad'], email=d['email'], 
                        sifre=hashli_sifre, brans_id=brans.id
                    )
                    db.session.add(yeni_doktor)
            
            if doktorlar_data:
                db.session.commit()
                print(f"{len(doktorlar_data)} adet varsayılan doktor eklendi.")
        
        # Eğer hiç randevu yoksa ve kullanıcılar varsa örnek bir randevu ekleyelim
        if not Randevu.query.first():
            hasta = Hasta.query.filter_by(email='hasta@hastane.com').first() # Varsayılan hastayı kullan
            doktor = Doktor.query.first()
            if hasta and doktor:
                db.session.add(Randevu(hasta_id=hasta.id, doktor_id=doktor.id, tarih=datetime.now() + timedelta(days=7, hours=10), sikayet="Örnek şikayet", durum="Bekleniyor"))
                db.session.commit()
                print("Örnek randevu eklendi.")

    app.run(debug=True) # Geliştirme modunu açar
