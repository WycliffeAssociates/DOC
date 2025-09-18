export type PassagesDocumentRequest = {
  langCode: string
  langName: string
  bibleReferences: Array<BibleReference>
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
