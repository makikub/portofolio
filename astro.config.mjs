import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  integrations: [tailwind()],
  site: 'https://yourdomain.com', // Firebase Hostingのドメインに後で変更
  build: {
    assets: 'assets'
  }
});

