/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: {
          900: '#0B0E14', // Primary Deep Dark
          800: '#151921', // Surface/Card
          700: '#1C222D', // Hover/Active
        },
        silver: {
          400: '#9CA3AF', // Muted Silver
          300: '#E5E7EB', // Bright Silver
          100: '#F9FAFB', // Text Silver
        },
      },
      backgroundImage: {
        'silver-gradient': 'linear-gradient(to right, #9CA3AF, #E5E7EB)',
      },
    },
  },
  plugins: [],
}
