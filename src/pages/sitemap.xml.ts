import type { APIRoute } from 'astro';
import staticRoutes from '../data/sitemap-routes.json';

type Article = { id: string };

export const GET: APIRoute = ({ site }) => {
  if (!site) throw new Error('Astro site must be configured for sitemap generation');
  const modules = import.meta.glob('../data/articles/*.json', {
    eager: true,
    import: 'default',
  });
  const articles = Object.values(modules) as Article[];
  const routes = [...staticRoutes, ...articles.map(({ id }) => `/notes/${id}/`)];
  const escapeXml = (value: string) => value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const entries = [...new Set(routes)].map(route => `<url><loc>${escapeXml(new URL(route, site).href)}</loc></url>`);
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entries.join('\n')}\n</urlset>\n`, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
