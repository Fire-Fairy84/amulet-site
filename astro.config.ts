import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://amulet.cards',
  output: 'static',
  trailingSlash: 'always',
  integrations: [
    mdx(),
    sitemap({ filter: (page) => !page.includes('/404') && !page.includes('/proximamente/') && !page.includes('/guides/') && !page.includes('/guias/') }),
  ],
});
