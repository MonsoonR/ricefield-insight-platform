import animate from 'tailwindcss-animate';

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{vue,ts,tsx,js,jsx}'],
  theme: {
    extend: {
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        chart: {
          1: 'hsl(var(--chart-1))',
          2: 'hsl(var(--chart-2))',
          3: 'hsl(var(--chart-3))',
          4: 'hsl(var(--chart-4))',
          5: 'hsl(var(--chart-5))',
        },
        rice: {
          primary: 'var(--rf-primary)',
          'primary-hover': 'var(--rf-primary-hover)',
          'primary-soft': 'var(--rf-primary-soft)',
          teal: 'var(--rf-teal)',
          'teal-soft': 'var(--rf-teal-soft)',
          gold: 'var(--rf-rice-gold)',
          'gold-soft': 'var(--rf-rice-gold-soft)',
          success: 'var(--rf-success)',
          'success-soft': 'var(--rf-success-soft)',
          warning: 'var(--rf-warning)',
          'warning-soft': 'var(--rf-warning-soft)',
          error: 'var(--rf-error)',
          'error-soft': 'var(--rf-error-soft)',
          info: 'var(--rf-info)',
          'info-soft': 'var(--rf-info-soft)',
          surface: 'var(--rf-surface)',
          border: 'var(--rf-border)',
        },
      },
    },
  },
  plugins: [animate],
};
