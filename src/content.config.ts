import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const paragraphs = z.array(z.string().min(1));
const orientation = z.object({
  keywords: paragraphs,
  essay: paragraphs,
  work: paragraphs,
  love: paragraphs,
  self: paragraphs,
  note: paragraphs,
});
const translation = z.object({
  slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  name: z.string().min(1),
  seoTitle: z.string().min(1),
  seoDescription: z.string().min(1),
  summary: z.string().min(1),
  imageDescription: z.string().min(1).nullable(),
  upright: orientation,
  reversed: orientation.extend({ summary: z.string().min(1) }),
});

const cards = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/cards' }),
  schema: z.object({
    id: z.string().min(1),
    number: z.number().int().nonnegative(),
    order: z.number().int().nonnegative(),
    arcana: z.enum(['major', 'minor']),
    suit: z.enum(['cups', 'pentacles', 'swords', 'wands']).nullable(),
    rank: z.number().int().min(1).max(14).nullable(),
    image: z.string().startsWith('/assets/cards/'),
    imageWidth: z.number().int().positive(),
    imageHeight: z.number().int().positive(),
    relatedCardIds: z.array(z.string()),
    sourceFiles: z.object({ en: z.string(), es: z.string() }),
    translations: z.object({ en: translation, es: translation }),
  }),
});

const guides = defineCollection({
  loader: glob({ pattern: '**/*.(md|mdx)', base: './src/content/guides' }),
  schema: z.object({
    translationId: z.string().min(1),
    language: z.enum(['en', 'es']),
    slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
    title: z.string().min(1),
    description: z.string().min(1),
    date: z.coerce.date(),
    socialImage: z.string().startsWith('/').optional(),
    relatedGuideIds: z.array(z.string()).default([]),
  }),
});

export const collections = { cards, guides };
