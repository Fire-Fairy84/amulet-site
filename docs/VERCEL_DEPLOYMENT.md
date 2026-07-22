# Despliegue en Vercel

Vercel es el único hosting de producción de `amulet.cards`. GitHub Pages está desactivado y no conserva workflow de despliegue ni archivo `CNAME`.

## Proyecto

- Cuenta: `fire-fairy84s-projects`
- Proyecto: `amulet-site`
- Framework: Astro
- Comando: `npm run build`
- Salida: `dist`
- Producción de control: `https://amulet-site.vercel.app`
- Preview comprobada durante el corte: `https://amulet-site-60qk00b3k-fire-fairy84s-projects.vercel.app`
- Dominio canónico: `https://amulet.cards`
- `www.amulet.cards` redirige permanentemente (308) a `amulet.cards`.

El sitio es completamente estático. Los previews de Vercel pueden estar protegidos por autenticación; canonical, hreflang, Open Graph y sitemap siempre usan el dominio público, nunca el hostname del preview.

## DNS externo

El DNS autoritativo se gestiona en Porkbun. Tras el corte, Vercel confirmó como válida esta configuración activa:

| Tipo | Nombre | Valor | TTL recomendado |
| --- | --- | --- | --- |
| A | `@` | `216.198.79.1` | 600 |
| CNAME | `www` | `b35cc95351fd3f11.vercel-dns-017.com` | 600 |

Se eliminaron los cuatro A anteriores de GitHub Pages (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`) y se sustituyó el CNAME `www → fire-fairy84.github.io`. No se cambiaron los nameservers ni registros de otros servicios. Vercel también muestra `64.29.17.1` como A secundario recomendado; el dominio figura `configured-correctly` con el registro activo anterior.

Los valores anteriores son los registros project-specific recomendados por Vercel para este proyecto. Antes de un cambio futuro, volver a ejecutar:

```bash
npx vercel domains verify amulet.cards
npx vercel domains verify www.amulet.cards
```

## Corte sin interrupción realizado

1. Ejecutar `npm ci`, `npm run typecheck`, `npm run lint` y `npm run build`.
2. Desplegar y validar `https://amulet-site.vercel.app`.
3. Asociar ambos dominios al proyecto y configurar `www` como redirect 308 al apex.
4. Cambiar únicamente los registros web descritos arriba.
5. Esperar a que Vercel confirme configuración válida y certificado TLS.
6. Validar landing, índices, cartas, assets, redirects históricos, robots y sitemap en `https://amulet.cards`.
7. Solo entonces desactivar GitHub Pages y retirar su workflow y `public/CNAME`.

La secuencia se completó en ese orden. `https://amulet.cards`, HTTP→HTTPS, `www`→apex, las 163 URLs canónicas y las 156 rutas históricas se validaron antes de retirar Pages.

## Rollback

Si fuera necesario volver temporalmente a GitHub Pages:

1. Recuperar `.github/workflows/deploy-pages.yml` y `public/CNAME` desde el historial de Git.
2. Volver a habilitar Pages con GitHub Actions y esperar a que el sitio termine de publicarse.
3. Restaurar los cuatro registros A del apex:
   - `185.199.108.153`
   - `185.199.109.153`
   - `185.199.110.153`
   - `185.199.111.153`
4. Restaurar `www CNAME fire-fairy84.github.io`.
5. Esperar la propagación y comprobar HTTPS.

No se deben alternar los registros de GitHub y Vercel simultáneamente: repartiría tráfico entre dos plataformas con comportamiento distinto para las redirecciones históricas.

## Despliegues posteriores

Con el repositorio conectado a Vercel, un push a `main` crea producción y las demás ramas producen previews. Para una comprobación local equivalente:

```bash
npm install
npm run dev
npm run build
npm run preview
```

Para auditar el dominio público después de un despliegue:

```bash
npm run validate:production
```

El script comprueba las 163 URLs canónicas, las 156 rutas históricas, sitemap, robots, páginas `noindex`, metadatos y assets representativos. Puede probarse el mismo artefacto antes del cambio DNS indicando el alias estable de Vercel:

```bash
npm run validate:production -- https://amulet-site.vercel.app
```

Los redirects históricos se mantienen como patrones en `vercel.json`; no se enumeran 156 entradas manuales. Para añadir un redirect nuevo, se incorpora una regla permanente con origen y destino terminados en `/`, se ejecutan `npm run build` y `npm run validate:production`, y se comprueba el código 308 tras desplegar.

No hay variables de entorno necesarias para construir el sitio actual. Los archivos `.vercel/`, `.env` y `.env.*` son locales y nunca deben versionarse.
