/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontSize: {
        base: ["18px", { lineHeight: "1.6" }],
      },
    },
  },
  plugins: [],
};
