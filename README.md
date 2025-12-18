# 🌱 Garden - Personal Growth Social Platform

> A positive-focused social video platform with ephemeral content and privacy-first design

[![Status](https://img.shields.io/badge/status-mvp-yellow)]() 
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

---

## 🎯 What is Garden?

Garden is a mental health and personal growth social platform that combines:
- 📹 **Short-form video** sharing (TikTok-style feed)
- ⏰ **Ephemeral content** (24-hour posts, 7-day comments)
- 🔒 **Privacy-first** architecture (control who sees what)
- 🌱 **Positive community** (negativity naturally expires)
- 🤝 **Peer support** (connect with others on similar growth journeys)

**Why it matters**: Traditional social media amplifies negativity. Garden's expiration model means encouraging content thrives while toxic content fades away.

---

## ✨ Features

| Feature | Status | Description |
|---------|--------|-------------|
| 📱 Video Posts | ✅ MVP | Upload videos (stored in Cloudflare R2) |
| ⏱️ 24hr Expiration | ✅ MVP | Posts disappear after 24 hours |
| 💬 Comments | ✅ MVP | 7-day expiring comments with upvote/downvote |
| 💧 Likes (Watering) | ✅ MVP | Symbolic Garden metaphor |
| 👥 Follow System | ✅ MVP | Follow others, friends-only privacy |
| 📊 User Profiles | ✅ MVP | View user stats and posts |
| 🔐 Auth0 Login | ✅ MVP | Secure authentication |
| 🤖 For You Page | 🔨 Planned | Personalized feed algorithm |
| 🔇 Content Moderation | 🔨 Planned | AI-powered NSFW filtering |

---

## 🏗️ Tech Stack

### Frontend
- React 18 + Vite
- TailwindCSS
- Auth0 React SDK
- Axios

### Backend
- FastAPI (Python 3.11)
- PostgreSQL / SQLite
- SQLAlchemy ORM
- Alembic migrations
- Auth0 JWT validation

### Infrastructure
- Docker + Docker Compose
- Cloudflare R2 (video storage)
- Mux (video encoding - planned)

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Auth0 account (free tier works)

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/community-app.git
cd community-app
```

### 2. Configure Auth0

1. Create an [Auth0 account](https://auth0.com)
2. Create a **Single Page Application**
3. Create an **API** with identifier: `https://api.garden-platform.com`
4. Copy credentials to `.env` files (see below)

### 3. Environment Variables

```bash
# Root directory
cp .env.example .env

# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

Edit each `.env` file and fill in your Auth0 credentials.

### 4. Start Services

```bash
docker-compose up -d
```

### 5. Initialize Database

```bash
docker-compose exec backend alembic upgrade head
```

### 6. Access Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📖 Documentation

- [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md) - Pre-launch checklist
- [`MVP_DEPLOYMENT_GUIDE.md`](MVP_DEPLOYMENT_GUIDE.md) - Full deployment guide
- [API Documentation](http://localhost:8000/docs) - Swagger UI (after running)

---

## 🤝 Contributing

**Garden is in active development!** Contributions are welcome:

- 🐛 Report bugs via [Issues](https://github.com/krillavilla/community-app/issues)
- 💡 Suggest features
- 🔧 Submit pull requests

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 💖 Support Development

Garden is built by an independent developer rebuilding his career while caring for his newborn son. If you believe in creating healthier social spaces:

- ⭐ Star this repo
- 🐦 Share on social media
- ☕ [Support on Ko-fi](https://ko-fi.com/krillavilla)
- 💜 [GitHub Sponsors](https://github.com/sponsors/krillavilla)

**Where donations go**: Cloud hosting, API costs, and development tools.

---

## 📊 Project Status

**Current Stage**: 80% MVP complete, preparing for user testing

| Milestone | Status |
|-----------|--------|
| Core API | ✅ Complete |
| Frontend Components | 🔨 In Progress |
| Video Upload | ✅ Complete |
| Expiration Worker | ✅ Complete |
| Rate Limiting | ⏳ Planned |
| Content Moderation | ⏳ Planned |
| Mobile App | 💭 Future |

---

## 🔒 Privacy & Security

Garden takes privacy seriously:
- ✅ GDPR-compliant (data export/deletion endpoints)
- ✅ Age verification (COPPA compliant)
- ✅ Auth0 authentication (industry-standard)
- ✅ Soft-delete architecture (30-day retention)
- 🔨 Screenshot detection (planned)
- 🔨 View tracking with consent (planned)

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Auth0 for authentication infrastructure
- Cloudflare for R2 storage
- The open-source community

---

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/krillavilla/community-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/krillavilla/community-app/discussions)

---

**Built with 💚 for healthier social spaces**
