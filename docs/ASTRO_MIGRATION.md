# Migración de amulet.cards a Astro

## Estado anterior

El repositorio era un sitio HTML estático publicado desde la raíz de `main` mediante GitHub Pages (modo `legacy`). El dominio se configuraba con `CNAME`; DNS apuntaba a `fire-fairy84.github.io` y a las IP de GitHub Pages. No existían `package.json`, configuración de Astro, `vercel.json` ni proyecto Vercel detectable en el repositorio.

La landing inglesa vivía en `/`, la española en `/es/`, las páginas de cartas españolas en `/tarot/{slug}/` y las inglesas en `/en/tarot/{slug}/`. Privacidad, términos y la página de “próximamente” también se han conservado.

## Arquitectura nueva

- Astro 7 con TypeScript estricto, `output: "static"`, `site: "https://amulet.cards"` y `trailingSlash: "always"`.
- `src/content/cards/*.json`: una entrada validada por carta, con las dos traducciones relacionadas.
- `src/components/CardPage.astro`: única plantilla para las páginas inglesas y españolas.
- `src/pages/en/cards/[slug].astro` y `src/pages/es/cartas/[slug].astro`: generación con `getStaticPaths()`.
- `src/lib/i18n.ts`: rutas, URLs absolutas y etiquetas de interfaz centralizadas.
- `src/content/guides/`: colección preparada para Markdown y MDX. Los índices vacíos se publican con `noindex` y salen del sitemap hasta que exista una guía real.
- `public/assets/cards/`: las 78 ilustraciones SVG verificadas de Amulet.

La landing conserva su estructura, textos, imágenes, paleta, tipografía, responsive y animaciones CSS. Se retiró únicamente la redirección automática por idioma basada en `navigator.language`; `/`, `/en/` y `/es/` quedan accesibles de forma explícita y sin JavaScript obligatorio. La landing enlaza discretamente al índice correspondiente.

El sitio HTML anterior se conserva de forma recuperable en `legacy-static/`. No participa en el build ni debe publicarse; sirve únicamente como referencia de migración y registro de las rutas históricas.

## Rutas

- `/` — landing principal y `x-default`.
- `/en/`, `/es/` — landings explícitas por idioma.
- `/en/cards/`, `/es/cartas/` — índices completos.
- `/en/cards/{slug}/`, `/es/cartas/{slug}/` — 78 páginas por idioma.
- `/en/guides/`, `/es/guias/` — índices futuros; `noindex` mientras estén vacíos.
- `/privacy/`, `/terms/`, `/proximamente/`, `/404.html` — rutas conservadas.

Vercel aplica redirecciones permanentes desde `/tarot/` y `/tarot/:slug` a `/es/cartas/`, y desde `/en/tarot/` y `/en/tarot/:slug` a `/en/cards/`. Los slugs históricos se mantienen, por lo que no hace falta una tabla carta a carta.

## Desarrollo

```bash
npm install
npm run migrate:cards
npm run dev
npm run typecheck
npm run build
npm run preview
```

`npm run migrate:cards` busca por defecto la app en el repositorio hermano `../amulet`. Puede indicarse otra ubicación:

```bash
AMULET_APP_ROOT=/ruta/a/amulet npm run migrate:cards
# o solo el corpus:
AMULET_CORPUS=/ruta/a/ArcanaCorpus npm run migrate:cards
```

En Vercel no es necesario clonar la app: `npm run validate:content` valida las entradas y assets ya generados cuando el checkout fuente no está disponible. Cuando sí está disponible, también comprueba que el contenido generado siga exactamente sincronizado.

## Vercel y despliegue

Vercel detecta Astro. `vercel.json` fija el comando `npm run build`, la salida `dist`, trailing slashes, caché de assets y redirecciones históricas. No se usa adapter porque el sitio es completamente estático y Vercel admite Astro estático sin configuración adicional.

Antes de cambiar DNS:

1. Importar `Fire-Fairy84/amulet-site` en Vercel.
2. Confirmar framework Astro, build `npm run build`, output `dist` y Node compatible con `package.json`.
3. Verificar un preview y las redirecciones.
4. Añadir `amulet.cards` al proyecto Vercel.
5. Cambiar los registros DNS siguiendo los valores exactos que muestre Vercel.
6. Esperar certificado TLS y verificar `https://amulet.cards` antes de desactivar GitHub Pages.

El dominio no puede migrarse solo con cambios de código. No hay variables de entorno web actuales que conservar; `APP_STORE_URL` pertenecía al generador antiguo y la web sigue mostrando el estado real “próximamente”.

## Guías futuras

Añadir un `.md` o `.mdx` bajo `src/content/guides/` con frontmatter:

```yaml
translationId: choosing-a-tarot-deck
language: en
slug: choosing-a-tarot-deck
title: Choosing a tarot deck
description: ...
date: 2026-08-01
socialImage: /assets/example.png # opcional y existente
relatedGuideIds: []
```

Después se añadirá una ruta dinámica de detalle que use `translationId` para canonical/hreflang. Los índices ya consultan la colección y pasarán automáticamente a `index, follow` cuando exista contenido real.

## Límites conocidos

- El corpus no incluye pregunta de journaling separada, autor humano, fechas editoriales ni relaciones explícitas entre cartas. No se han inventado.
- Las fuentes Cormorant y Hanken Grotesk siguen cargándose desde Google Fonts, igual que antes; no hay archivos locales de fuente en los repositorios inspeccionados.
- El cambio efectivo de GitHub Pages a Vercel y el DNS requieren acciones manuales.
