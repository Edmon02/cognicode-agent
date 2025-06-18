/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'export', // Commented out to allow server-side features
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { unoptimized: true },
  experimental: {
    esmExternals: 'loose',
  },
  webpack: (config, { isServer }) => {
    // Handle socket.io client-side only
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        net: false,
        tls: false,
        fs: false,
      };
    }
    
    // Ignore node-specific modules on client side
    config.externals = config.externals || [];
    if (!isServer) {
      config.externals.push({
        'bufferutil': 'bufferutil',
        'utf-8-validate': 'utf-8-validate',
      });
    }
    
    return config;
  },
};

module.exports = nextConfig;
