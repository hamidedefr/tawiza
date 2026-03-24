# Frontend Tawiza

Dashboard Next.js 14 avec shadcn/ui, Tailwind CSS et Recharts.

## Lancer

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Le frontend tourne sur http://localhost:3000.

## Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- SWR (data fetching)
- Recharts + D3.js (visualisations)

## Variables d'environnement

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | URL du backend |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000/ws` | URL WebSocket |
| `NEXT_PUBLIC_TELEMETRY_ENABLED` | `true` | Telemetrie anonyme |

## Structure

```
frontend/
├── app/dashboard/     # Pages du dashboard
├── components/        # Composants React (shadcn/ui)
├── hooks/             # Hooks SWR + custom
├── lib/               # Utilitaires
└── public/            # Assets statiques
```

Basé sur [shadcn-nextjs-boilerplate](https://github.com/horizon-ui/shadcn-nextjs-boilerplate) (MIT).
