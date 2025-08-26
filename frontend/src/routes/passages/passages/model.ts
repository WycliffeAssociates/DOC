import { z } from 'zod'

export const BibleReferenceSchema = z.object({
  book_code: z.string(),
  book_name: z.string(),
  start_chapter: z.number(),
  start_chapter_verse_ref: z.string(),
  end_chapter: z.number().nullable().optional(),
  end_chapter_verse_ref: z.string().nullable().optional()
})

export type BibleReference = z.infer<typeof BibleReferenceSchema>
