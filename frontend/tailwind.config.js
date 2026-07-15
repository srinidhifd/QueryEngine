/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-teal': '#00c6c2',
        'midnight-black': '#052831',
        'card-dark': '#0d1117',
        'text-secondary': '#ffffff',
        'placeholder-muted': '#8b8b8b',
      },
      fontFamily: {
        heading: ['Segoe UI', 'Arial', 'sans-serif'],
        body: ['Avenir Next LT Pro', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
}
