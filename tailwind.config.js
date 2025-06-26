// tailwind.config.js
const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'text': 'var(--color-text)',
        'background': 'var(--color-background)',
        'background-secondary': 'var(--color-background-secondary)',
        'sidenav-primary': 'var(--color-sidenav-primary)',
        'sidenav-secondary': 'var(--color-sidenav-secondary)',
        'sidenav-tertiary': 'var(--color-sidenav-tertiary)',
        'primary': 'var(--color-primary)',
        'secondary': 'var(--color-secondary)',
        'tertiary': 'var(--color-tertiary)',
        'accent': 'var(--color-accent)',
        'input-txt': 'var(--color-input-txt)',
        'info-txt': 'var(--color-info-txt)',
        'button-sec': 'var(--button-sec)',
      },
    },
  },
  plugins: [
    require('tailwind-scrollbar'),
  ],
};


// 'inside-button': '#4bb5f5', 
// 'outside-button': '#000000',
// 'general-bgcolor': '#172442',
// 'navbar-bgcolor': '#141f38',
// 'component-colors' : '#090f1c',
// 'test-color': '#292b66',
// 'msg-color': '#212f4f',
// 'msgbox-border': '#4bb5f5',

//#141f38 primary/bg
//#4b5c82 secondary/p
//#090f1c