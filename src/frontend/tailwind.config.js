/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4f46e5',
        secondary: '#9333FA',
        success: '#10B981',
        danger: '#ef4444',
        gray: {
          200: '#e5e7eb',
          500: '#9CA3AF',
          800: '#1f2937',
        },
      },
    },
  },
  plugins: [],
}