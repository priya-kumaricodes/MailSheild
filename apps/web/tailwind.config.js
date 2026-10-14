/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        shield: {
          bg: '#080c14',
          surface: '#0d1527',
          card: '#131e36',
          cardHover: '#182544',
          border: '#1f2e4d',
          borderLight: '#2d3f66',
          accent: '#6366f1',
          cyan: '#06b6d4',
          spam: '#f43f5e',
          spamBg: 'rgba(244, 63, 94, 0.1)',
          ham: '#10b981',
          hamBg: 'rgba(16, 185, 129, 0.1)',
          gold: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 15px rgba(99, 102, 241, 0.2)' },
          '100%': { boxShadow: '0 0 30px rgba(6, 182, 212, 0.4)' },
        }
      }
    },
  },
  plugins: [],
};
