# Modelo de contenido de cartas

## Fuente y recuento

La fuente original permanece sin modificaciones en `../amulet/Resources/ArcanaCorpus/`: 156 Markdown, 78 en inglés y 78 en español. La baraja real contiene 78 cartas: 22 arcanos mayores y 56 menores, agrupados en cups/copas, pentacles/oros, swords/espadas y wands/bastos.

Las ilustraciones proceden de assets reales de marketing de la app: 22 SVG de mayores y 56 SVG de menores. El script los copia a nombres estables basados en el ID de la carta.

## Entrada JSON

Cada archivo de `src/content/cards/` representa una carta y contiene:

- `id`: identificador estable compartido entre idiomas.
- `number`, `rank`, `order`: número editorial, rango y orden total explícito.
- `arcana`: `major` o `minor`.
- `suit`: `cups`, `pentacles`, `swords`, `wands` o `null`.
- `image`, `imageWidth`, `imageHeight`: asset comprobable y dimensiones.
- `relatedCardIds`: relaciones explícitas; actualmente vacío porque el corpus no las declara.
- `sourceFiles`: nombres de los dos Markdown originales para trazabilidad.
- `translations.en` y `translations.es`: slug, nombre, SEO y texto editorial.

Cada orientación conserva los campos reales del corpus: `keywords`, `essay`, `work`, `love`, `self` y `note`. La orientación invertida incluye además su `summary`. Los arrays vacíos no se publican; la plantilla omite la sección correspondiente.

Los títulos SEO se forman de manera determinista con el nombre real de la carta. Las descriptions reutilizan íntegramente `reads as`; no se generan interpretaciones nuevas.

## Campos ausentes

No existen en la fuente actual y por tanto no se publican:

- journaling prompt independiente;
- autor o fecha editorial verificables;
- asociaciones explícitas entre cartas;
- ratings, reseñas o precio de la app;
- imágenes diferentes por idioma;
- una sección separada de “carrera” distinta de `work`;
- afirmaciones predictivas o profesionales.

## Regenerar y validar

```bash
npm run migrate:cards
npm run validate:content
```

El migrador:

1. lee los Markdown originales;
2. asocia inglés y español por clave estable;
3. normaliza secciones y párrafos;
4. exige título, resumen y ensayo en ambas orientaciones;
5. detecta IDs y slugs duplicados;
6. detecta traducciones, imágenes o relaciones ausentes;
7. escribe JSON UTF-8 y copia SVG;
8. falla con un mensaje concreto ante inconsistencias.

Para probar la arquitectura sin reescribir todo: `python3 scripts/migrate_cards.py --limit 2`. Para volver al estado completo, ejecutar después `npm run migrate:cards`.

## Añadir o modificar una carta

1. Editar la fuente original en la app, nunca el Swift ni el contenido generado para esta tarea.
2. Añadir los dos Markdown con su nomenclatura coherente y el SVG correspondiente.
3. Si es una carta estructuralmente nueva, ampliar los mapas del migrador con su ID, orden y slugs públicos.
4. Ejecutar `npm run migrate:cards` y `npm run build`.
5. Si cambia un slug ya público, conservar el anterior en `vercel.json` como redirección permanente a la nueva URL.

No se debe editar un JSON generado para hacer cambios editoriales permanentes: la siguiente migración lo sobrescribirá.
