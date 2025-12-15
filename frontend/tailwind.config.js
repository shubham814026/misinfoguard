/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        crypto: {
          50: '#fdf8f3',
          100: '#f9ede0',
          200: '#f3d9c0',
          300: '#e9bf96',
          400: '#dea169',
          500: '#d4864b',
          600: '#c06d3f',
          700: '#a05636',
          800: '#824632',
          900: '#6b3b2b',
          950: '#3a1d15',
        },
        brown: {
          50: '#faf8f5',
          100: '#f0ebe3',
          200: '#e1d5c5',
          300: '#cbb89e',
          400: '#b69879',
          500: '#a6825f',
          600: '#997053',
          700: '#7f5b45',
          800: '#6a4c3c',
          900: '#584133',
          950: '#2f221a',
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'crypto-gradient': 'linear-gradient(135deg, #3a1d15 0%, #6b3b2b 50%, #a05636 100%)',
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.6s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(212, 134, 75, 0.5), 0 0 10px rgba(212, 134, 75, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(212, 134, 75, 0.8), 0 0 30px rgba(212, 134, 75, 0.4)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
