import { z } from 'zod'

export const BibleReferenceDtoSchema = z
  .object({
    lang_code: z.string().nullable(),
    book_code: z.string(),
    book_name: z.string(),
    start_chapter: z.number(),
    start_chapter_verse_ref: z.string(),
    end_chapter: z.number().nullable(),
    end_chapter_verse_ref: z.string().nullable()
  })
  .transform((dto) => ({
    langCode: dto.lang_code,
    bookCode: dto.book_code,
    bookName: dto.book_name,
    startChapter: dto.start_chapter,
    startChapterVerseRef: dto.start_chapter_verse_ref,
    endChapter: dto.end_chapter,
    endChapterVerseRef: dto.end_chapter_verse_ref
  }))

export const parseBibleReferences = z.array(BibleReferenceDtoSchema)

export type BibleReference = z.infer<typeof BibleReferenceDtoSchema>

export function matches(a: BibleReference, b: BibleReference) {
  return (
    a.langCode === b.langCode &&
    a.bookCode === b.bookCode &&
    a.startChapter === b.startChapter &&
    a.startChapterVerseRef === b.startChapterVerseRef &&
    a.endChapter === b.endChapter &&
    a.endChapterVerseRef === b.endChapterVerseRef
  )
}

export type BibleReferenceWithAvailability = {
  reference: BibleReference // The original reference object
  isAvailable: boolean // Flag indicating if this reference is available (e.g., based on prior checks)
}

export type PassagesDocumentRequest = {
  lang0Code: string
  lang0Name: string
  lang1Code?: string | null
  lang1Name?: string | null
  bibleReferences: Array<BibleReferenceWithAvailability> // Now uses the wrapper
  emailAddress: string | null
}
