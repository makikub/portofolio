/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1a1a1a',
          light: '#4a4a4a',
        },
        secondary: {
          DEFAULT: '#6b6b6b',
          light: '#9b9b9b',
        },
        accent: {
          DEFAULT: '#f5f5f0',
          dark: '#e8e8e0',
        },
        beige: {
          50: '#fafaf8',
          100: '#f5f5f0',
          200: '#e8e8e0',
          300: '#d1d1c8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Georgia', 'serif'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '65ch',
            color: '#1a1a1a',
            a: {
              color: '#1a1a1a',
              '&:hover': {
                color: '#4a4a4a',
              },
            },
          },
        },
      },
    },
  },
  plugins: [],
};

