# ⚽ Global Football News Bot

**Tamamen ücretsiz, 24/7 otomatik çalışan, dünya çapındaki futbol haberlerini toplayan ve X'te paylaşan akıllı bot sistemi.**

## 🌟 Özellikler

### 📰 Kapsamlı Haber Toplama
- **120+ haber kaynağı** (6 dilde, 6 kıtadan)
- **Akıllı filtreleme** ve önceliklendirme
- **Otomatik çeviri** (Türkçe ↔ İngilizce)
- **Görsel çekme** (haberin orijinal görseli)
- **Spam koruması** ve tekrar önleme

### 🤖 Otomatik Sosyal Medya Paylaşımı  
- **2 X hesabı**: İngilizce + Türkçe
- **15 dakikada** bir güncelleme
- **Selenium automation** (ücretsiz)
- **İnsan benzeri** davranış
- **Günlük limitler** (güvenlik)

### 🌐 Modern Web Sitesi
- **2 dilli** arayüz (EN/TR)
- **Dark/Light** tema
- **Responsive** tasarım
- **Real-time** güncellemeler
- **REST API** desteği

### ☁️ Full Otomatik Deployment
- **GitHub Actions** (24/7 çalışma)
- **Vercel/Railway** hosting
- **Zero-cost** hosting seçenekleri
- **Auto-scaling** support

## 🚀 Hızlı Başlangıç

### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/your-username/football-news-bot.git
cd football-news-bot
```

### 2. Dependencies Kurun
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Ayarlayın
```bash
cp .env.example .env
# .env dosyasını X hesap bilgilerinizle düzenleyin
```

### 4. Test Edin (Lokal)
```bash
# Sadece haber toplama testi
python football_news_aggregator.py

# Web sitesi testi  
python web_app.py
# http://localhost:5000 adresinde açılacak
```

### 5. GitHub'a Deploy Edin
1. Repository'nizi GitHub'a push edin
2. GitHub Secrets'a X hesap bilgilerini ekleyin:
   - `X_ENGLISH_USERNAME`
   - `X_ENGLISH_PASSWORD` 
   - `X_TURKISH_USERNAME`
   - `X_TURKISH_PASSWORD`

3. GitHub Actions otomatik başlayacak! 🎉

## 📊 Sistem Mimarisi

```
┌─────────────────────────────────────────────────────┐
│                GitHub Actions (Ücretsiz)           │
│                   Her 15 Dakika                    │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│           Haber Toplama Servisi                    │
│  • 120+ RSS Feed                                   │
│  • Web Scraping                                    │  
│  • Görsel Çekme                                    │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│            Akıllı Filtreleme                       │
│  • Önem Puanlama                                  │
│  • Çeviri (6 Dil)                                 │
│  • Tekrar Temizleme                               │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────▼──────────────┐
    │     Selenium X Bot         │
    │  • İngilizce Hesap         │
    │  • Türkçe Hesap            │
    └─────────────┬──────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│              Web Sitesi (Vercel)                   │
│  • 2 Dilli Arayüz                                 │
│  • REST API                                        │
│  • Real-time Updates                               │
└─────────────────────────────────────────────────────┘
```

## 🗄️ Dosya Yapısı

```
football-news-bot/
├── 📊 Veri İşleme
│   ├── global_football_sources.json     # Haber kaynakları
│   ├── football_news_aggregator.py      # Ana toplama servisi
│   ├── news_filter.py                   # Akıllı filtreleme
│   └── translation_manager.py           # Çeviri sistemi
│
├── 🤖 Automation
│   └── x_automation_bot.py              # X paylaşım botu
│
├── 🌐 Web App  
│   ├── web_app.py                       # Flask backend
│   └── templates/index.html             # Frontend
│
├── ⚙️ DevOps
│   ├── .github/workflows/               # GitHub Actions
│   ├── requirements.txt                 # Python dependencies
│   └── .env.example                     # Environment template
│
└── 📚 Documentation
    └── README.md                        # Bu dosya
```

## 🔧 Yapılandırma

### Haber Kaynakları Ekleme
`global_football_sources.json` dosyasını düzenleyerek yeni kaynaklar ekleyebilirsiniz:

```json
{
  "english_sources": {
    "new_category": [
      {
        "name": "Kaynak Adı",
        "rss": "https://example.com/rss.xml",
        "priority": 8,
        "region": "europe"
      }
    ]
  }
}
```

### X Bot Ayarları
`x_automation_bot.py` içinde günlük tweet limitlerini ayarlayabilirsiniz:

```python
DAILY_LIMITS = {
    'english': 30,  # İngilizce hesap için günlük limit
    'turkish': 30   # Türkçe hesap için günlük limit
}
```

### GitHub Actions Sıklığı
`.github/workflows/football-news-bot.yml` içinde çalışma sıklığını değiştirebilirsiniz:

```yaml
schedule:
  - cron: '*/15 * * * *'  # Her 15 dakika (değiştirilebilir)
```

## 📈 İzleme ve Loglar

### GitHub Actions Logları
- Repository → Actions sekmesi
- Her çalışmanın detaylı logları
- Hata bildirimleri

### Web Dashboard
```bash
# Lokal test
python web_app.py
# http://localhost:5000/api/stats -> İstatistikler
# http://localhost:5000/api/health -> Sistem durumu
```

### Manuel Tetikleme
```bash
# GitHub Actions'ı manuel başlatma
gh workflow run football-news-bot.yml

# Veya Python ile:
python football_news_aggregator.py
```

## 🛠️ Troubleshooting

### X Hesabı Banlandı?
1. Yeni hesap oluşturun
2. GitHub Secrets'ı güncelleyin
3. Bot yeni hesabı otomatik kullanacak

### Haber Çekilmiyor?
```bash
# Test edin:
python -c "from football_news_aggregator import *; a=FootballNewsAggregator(); print(len(a.fetch_all_news()))"
```

### Web Sitesi Açılmıyor?
```bash
# Dependencies kontrol:
pip install -r requirements.txt

# Flask test:
export FLASK_ENV=development
python web_app.py
```

### GitHub Actions Çalışmıyor?
1. Repository Settings → Actions → Enable
2. Secrets'ların doğru tanımlandığını kontrol edin
3. `latest_football_news.json` commit edildiğini kontrol edin

## 💰 Maliyet Analizi

| Servis | Ücret | Limit |
|--------|-------|-------|
| GitHub Actions | **0₺** | 2000 dakika/ay |
| Vercel Hosting | **0₺** | 100 site |
| RSS Feeds | **0₺** | Sınırsız |
| Çeviri API | **0₺** | Rotasyon sistemi |
| X Accounts | **0₺** | Manuel oluşturma |
| Chrome/Selenium | **0₺** | Open source |

**Toplam: 0₺/ay** ✨

## 🔒 Güvenlik

- **Credentials** GitHub Secrets'te şifrelenir
- **Rate limiting** ile API koruması  
- **Human-like** bot davranışı
- **IP rotation** desteği
- **Error handling** ve recovery

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında yayınlanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙋‍♂️ Destek

Sorularınız için:
- 🐛 **Bug Report**: GitHub Issues
- 💡 **Feature Request**: GitHub Discussions  
- 📧 **Email**: your-email@example.com
- 🐦 **Twitter**: [@your_account](https://twitter.com/your_account)

## 🎯 Roadmap

### Versiyon 2.0
- [ ] WhatsApp Business API entegrasyonu
- [ ] Telegram kanal desteği
- [ ] Video highlight üretimi
- [ ] AI-powered haber özeti
- [ ] Mobile app (React Native)

### Versiyon 3.0  
- [ ] Machine Learning haber önceliklendirme
- [ ] Kullanıcı özelleştirme
- [ ] Premium abonelik sistemi
- [ ] Analytics dashboard
- [ ] Multi-language support (10+ dil)

---

⭐ **Beğendiyseniz star verin!** Bu projenin gelişmesine yardımcı olur.

🚀 **Deployed by:** [Your Name](https://github.com/your-username)
📅 **Last Updated:** $(date)