/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tactical: {
          950: '#060a0f',
          900: '#0b131e',
          850: '#101c2c',
          800: '#16253b',
          700: '#1f3554',
          border: '#1f3554',
          accent: '#06b6d4', // cyan-500
          emerald: '#10b981',
          amber: '#f59e0b',
          crimson: '#ef4444'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}
