import { writable } from 'svelte/store'
import type { PassageReferenceDto } from '../models/passage'

// Define the passages store
export const passagesStore = writable<PassageReferenceDto[]>([])

export const addPassageReference = (
  langCode: string,
  bookCode: string,
  bookName: string,
  startChapterNum: number,
  startChapterVerseReference: string,
  endChapterNum?: number | null,
  endChapterVerseReference?: string | null
) => {
  passagesStore.update((currentPassages) => {
    // Check if the passage already exists
    const exists = currentPassages.some(
      (p) =>
        p.langCode === langCode &&
        p.bookCode === bookCode &&
        p.startChapterNum === startChapterNum &&
        p.startChapterVerseReference === startChapterVerseReference &&
        p.endChapterNum === endChapterNum &&
        p.endChapterVerseReference === endChapterVerseReference
    )
    if (exists) {
      return currentPassages // Return unchanged if passage exists
    }
    return [
      ...currentPassages,
      {
        id: Math.max(0, ...currentPassages.map((p) => p.id)) + 1,
        langCode,
        bookCode,
        bookName,
        startChapterNum,
        startChapterVerseReference,
        endChapterNum,
        endChapterVerseReference
      }
    ]
  })
}
