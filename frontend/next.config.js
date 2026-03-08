/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  productionBrowserSourceMaps: true,

  // Configuration avancée pour le développement via IP/Tailscale
  serverExternalPackages: [],

  // Allow cross-origin requests from Tailscale IPs in dev mode
  // Format Next.js 15.x: hostnames only (no protocol or port)
  allowedDevOrigins: [
    '100.105.242.48',
    '100.116.5.14',
    'localhost',
    '127.0.0.1',
    'moltbot-secure.tail87c07.ts.net',
    'hamidelamite.tail87c07.ts.net',
  ],

  // Correction pour les erreurs 403 et HMR sur IP externe
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
        ],
      },
    ];
  },

  // Rewrite /api/v1/* to FastAPI backend
  async rewrites() {
    const backendUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
      // Proxy pour le chat direct
      {
        source: '/api/tajine',
        destination: `${backendUrl}/api/v1/tajine/analyze`,
      },
      // Proxy collector micro-signals API
      {
        source: '/api/collector/:path*',
        destination: `${backendUrl}/api/collector/:path*`,
      },
    ];
  },

  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https', hostname: 'i.ibb.co' },
      { protocol: 'https', hostname: 'scontent.fotp8-1.fna.fbcdn.net' },
      { protocol: 'http', hostname: '100.116.5.14' },
      { protocol: 'https', hostname: '**.googleusercontent.com' },
    ],
  },
};

// Wrap with Sentry if available
let finalConfig = nextConfig;
try {
  const { withSentryConfig } = require('@sentry/nextjs');
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    finalConfig = withSentryConfig(nextConfig, {
      silent: true,
      hideSourceMaps: false,
    });
  }
} catch {
  // @sentry/nextjs not installed, skip
}

module.exports = finalConfig;
