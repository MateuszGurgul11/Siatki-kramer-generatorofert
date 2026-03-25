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
          green: '#0e6d4d',
          'green-dark': '#0a5440',
          'green-light': '#e6f2ef',
          'green-mid': '#2a9d7a',
        }
      }
    },
  },
  plugins: [],
}
