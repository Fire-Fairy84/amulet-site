# SEO de amulet.cards

## Canonical y hreflang

`SeoHead.astro` genera URLs absolutas. Cada página canónica apunta a sí misma. Las páginas de carta incluyen enlaces bidireccionales `en` y `es` a la misma carta usando sus slugs propios, además de `x-default` hacia `/`. Los índices y landings siguen el mismo principio.

No se usa canonical cruzado entre idiomas. La utilidad `src/lib/i18n.ts` concentra la construcción de rutas para impedir divergencias entre navegación, canonical y alternates.

La integración de sitemap no puede relacionar correctamente rutas con segmentos y slugs traducidos (`cards`/`cartas`, `the-fool`/`el-loco`). Por eso no se activa su opción i18n genérica: esa opción produciría alternates incorrectos. Las relaciones completas se publican en el HTML, mientras el sitemap contiene cada URL canónica una vez.

## Metadatos y datos estructurados

Todas las páginas indexables tienen title y description únicos, canonical absoluta, Open Graph, Twitter Card, favicon, Apple touch icon, theme color y robots. Las páginas de carta publican `Article` y `BreadcrumbList`; los índices publican `CollectionPage` con `ItemList`. Solo se incluyen organización, idioma, URL, imagen y texto verificables.

No se añaden autores humanos, ratings, precios, reseñas ni fechas inventadas. El contenido presenta el tarot como simbolismo, reflexión y exploración personal.

## Sitemap y robots

La build genera:

- `https://amulet.cards/sitemap-index.xml`
- `https://amulet.cards/sitemap-0.xml`

`robots.txt` apunta a `sitemap-index.xml` y permite explícitamente Googlebot y OAI-SearchBot. Se excluyen 404, `/proximamente/` y los índices vacíos de guías con `noindex`.

`npm run validate:site` compara las canonicals indexables con todas las URLs del sitemap, valida JSON-LD, alternates de cartas, assets, títulos, descriptions, h1 y enlaces internos.

En producción, ambos sitemaps y `robots.txt` se sirven desde Vercel con el dominio canónico. `sitemap-0.xml` contiene 163 URLs HTTPS únicas: portada, landings inglesa y española, ambos índices, 78 cartas inglesas, 78 españolas y las páginas legales. No contiene hostnames `vercel.app` ni `github.io`.

## Google Search Console

El cambio de hosting no cambia la propiedad de Search Console y no requiere la herramienta de cambio de dirección. Después del despliegue:

1. Abrir o confirmar `amulet.cards` como propiedad de dominio existente.
2. Conservar su TXT de verificación; si Google solicita uno nuevo, usar exactamente el que proporcione.
3. Enviar `https://amulet.cards/sitemap-index.xml`.
4. Solicitar indexación solo de `/`, `/en/cards/`, `/es/cartas/` y unas pocas cartas representativas.
5. Dejar que Google descubra el resto mediante sitemap y enlaces internos; no solicitar cientos de URLs manualmente.

Durante la auditoría DNS del corte no se observó un TXT de verificación en el apex, por lo que la verificación de la propiedad no pudo confirmarse desde el repositorio. Si Search Console la solicita, hay que añadir exactamente el TXT proporcionado por Google sin modificar los registros web de Vercel.

## Cambios de slug

Un slug público no se elimina sin redirección. Añadir una entrada permanente en `vercel.json`, desplegar, comprobar el status y conservar la redirección mientras la URL antigua tenga enlaces o historial de indexación.

## Comprobaciones

```bash
npm run typecheck
npm run lint
npm run build
git diff --check
```

La build ejecuta automáticamente la validación de contenido antes de Astro y la auditoría HTML/sitemap después.
