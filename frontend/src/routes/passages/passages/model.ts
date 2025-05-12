import { z } from 'zod'

// export const LangDirEnum = z.enum(['ltr', 'rtl']) // Adjust as needed

export const BibleReferenceSchema = z.object({
  book_code: z.string(),
  book_name: z.string(),
  start_chapter: z.number(),
  start_chapter_verse_ref: z.string(),
  end_chapter: z.number().nullable().optional(),
  end_chapter_verse_ref: z.string().nullable().optional()
})

// export const Part1ItemSchema = z.object({
//   text: z.string(),
//   reference: z.string()
// })

// export const Part2ItemSchema = z.object({
//   reference: z.string(),
//   question: z.string(),
//   answer: z.string()
// })

// export const ParsedTextSchema = z.object({
//   bible_reference: BibleReferenceSchema,
//   background: z.string().nullable().optional(),
//   directive: z.string(),
//   part_1: z.array(Part1ItemSchema),
//   part_1_directive: z.string(),
//   part_2: z.array(Part2ItemSchema),
//   part_2_directive: z.string(),
//   comment_section: z.string().nullable().optional()
// })

// export const RGChapterSchema = z.object({
//   content: ParsedTextSchema
// })

// export const RGBookSchema = z.object({
//   lang_code: z.string(),
//   lang_name: z.string(),
//   book_code: z.string(),
//   resource_type_name: z.string(),
//   chapters: z.record(z.number(), RGChapterSchema),
//   lang_direction: LangDirEnum
// })

// Infer TypeScript types from schemas so that typescript
// can strictly type check. If you don't infer you will lose
// strict typing when using only zod to define typescript types.
// export type RGBook = z.infer<typeof RGBookSchema>
// export type RGChapter = z.infer<typeof RGChapterSchema>
// export type ParsedText = z.infer<typeof ParsedTextSchema>
// export type Part1Item = z.infer<typeof Part1ItemSchema>
// export type Part2Item = z.infer<typeof Part2ItemSchema>
export type BibleReference = z.infer<typeof BibleReferenceSchema>
