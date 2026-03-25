/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        kramer: {
          green: '#1a5c2a',
          'green-light': '#e8f5e9',
          'green-mid': '#4caf50',
        }
      }
    },
  },
  plugins: [],
}
