/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        mospiBlue: "#003366",
        mospiLightBlue: "#004e8c",
        mospiGold: "#f39c12",
      },
    },
  },
  plugins: [],
};
