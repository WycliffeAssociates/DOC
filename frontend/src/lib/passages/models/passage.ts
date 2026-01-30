export type PassagesDocumentRequest = {
  lang0Code: string
  lang0Name: string
  lang1Code?: string | null
  lang1Name?: string | null
  bibleReferences: Array<BibleReferenceWithAvailability> // Now uses the wrapper
  emailAddress: string | null
}

export type BibleReference = {
  id: number
  langCode: string
  bookCode: string
  bookName: string
  startChapter: number
  startChapterVerseRef: string
  endChapter?: number | null
  endChapterVerseRef?: string | null
}

export type BibleReferenceWithAvailability = {
  reference: BibleReference // The original reference object
  isAvailable: boolean // Flag indicating if this reference is available (e.g., based on prior checks)
}
