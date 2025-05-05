export type PassagesDocumentRequest = {
  langCode: string
  langName: string
  passageReferences: Array<PassageReferenceDto>
  emailAddress: string | null
}

export type PassageReferenceDto = {
  id: number
  langCode: string
  bookCode: string
  bookName: string
  startChapterNum: number
  startChapterVerseReference: string
  endChapterNum?: number | null
  endChapterVerseReference?: string | null
}
