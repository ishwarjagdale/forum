/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["templates/forum/**/*.{html,js}"],
  theme: {
    extend: {
      fontFamily: {
        Poppins: ['Poppins', 'sans-serif'],
        Rubik: ['Rubik', 'sans-serif'],
        Lato: ['Lato', 'sans-serif'],
        Roboto: ['Roboto', 'sans-serif'],
        SourceSerifPro: ['source-serif-pro', 'sans-serif']
      }
    },
  },
  plugins: [],
}