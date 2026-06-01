# Financial Dashboard - FinARG

Dashboard financiero personal con alertas automáticas a Telegram.

## Stack

- **Frontend:** Vue 3 + PrimeVue + Chart.js (modo oscuro)
- **Backend:** Python FastAPI
- **Bot:** Telegram (@finARG_bot)

## Estructura

```
FinancialAgent/
├── frontend/          # Vue 3 + Vite
│   ├── src/
│   │   ├── components/  # Sidebar
│   │   ├── views/       # Dashboard, Transactions, Alerts, Settings
│   │   ├── router/      # Vue Router
│   │   ├── App.vue
│   │   └── main.js
│   └── package.json
├── backend/           # FastAPI
│   ├── app/
│   │   ├── main.py        # API endpoints
│   │   ├── telegram_bot.py # Telegram integration
│   │   └── config.py      # Environment config
│   ├── .env
│   ├── requirements.txt
│   └── run.py
└── README.md
```

## Iniciar

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```
El servidor corre en http://localhost:8000

### Frontend
```bash
cd frontend
npm install
npm run dev
```
La app corre en http://localhost:5173


