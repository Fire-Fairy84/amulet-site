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

El sitio HTML anterior sigue disponible en el historial de Git como referencia de migración; no participa en el build ni se publica. Las rutas históricas se conservan en `vercel.json`.

## Rutas

- `/` — landing principal y `x-default`.
- `/en/`, `/es/` — landings explícitas por idioma.
- `/en/cards/`, `/es/cartas/` — índices completos.
- `/en/cards/{slug}/`, `/es/cartas/{slug}/` — 78 páginas por idioma.
- `/en/guides/`, `/es/guias/` — índices futuros; `noindex` mientras estén vacíos.
- `/privacy/`, `/terms/`, `/proximamente/`, `/404.html` — rutas conservadas.

Vercel aplica redirecciones permanentes desde `/tarot/` y `/tarot/:slug/` a `/es/cartas/`, y desde `/en/tarot/` y `/en/tarot/:slug/` a `/en/cards/`. Los slugs históricos se mantienen, por lo que no hace falta una tabla carta a carta.

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

Vercel no necesita clonar la app: `npm run validate:content` valida siempre las entradas y assets versionados, de modo que el build no dependa de un checkout hermano. `npm run validate:source` compara explícitamente el contenido generado con la app cuando su repositorio está disponible; `npm run migrate:cards` sigue siendo la única operación que escribe contenido.

## Vercel y despliegue

Vercel detecta Astro. `vercel.json` fija el comando `npm run build`, la salida `dist`, trailing slashes, caché de assets y redirecciones históricas. No se usa adapter porque el sitio es completamente estático y Vercel admite Astro estático sin configuración adicional. La configuración operativa, DNS y rollback se detallan en `docs/VERCEL_DEPLOYMENT.md`.

El proyecto de producción es `fire-fairy84s-projects/amulet-site`, conectado a `Fire-Fairy84/amulet-site` con `main` como rama de producción. `amulet.cards`, `www.amulet.cards` y el alias de control `amulet-site.vercel.app` están asignados al proyecto. Vercel sirve HTTPS y `www` redirige con 308 al dominio raíz.

GitHub Pages se desactivó después de verificar el dominio en Vercel. Se retiraron su workflow y `public/CNAME`; `.github/workflows/ci.yml` conserva build, typecheck, lint y validaciones sin publicar en una segunda plataforma.

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
