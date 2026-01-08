import { writable } from 'svelte/store'
import type { BibleReference } from '../models/passage'

// Define the passages store
export const passagesStore = writable<BibleReference[]>([])
export const filteredPassagesStore = writable<BibleReference[]>([])

export const addBibleReference = (
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
        p.startChapter === startChapterNum &&
        p.startChapterVerseRef === startChapterVerseReference &&
        p.endChapter === endChapterNum &&
        p.endChapterVerseRef === endChapterVerseReference
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
        startChapter: startChapterNum,
        startChapterVerseRef: startChapterVerseReference,
        endChapter: endChapterNum,
        endChapterVerseRef: endChapterVerseReference
      }
    ]
  })
}

export const addFilteredBibleReference = (
  langCode: string,
  bookCode: string,
  bookName: string,
  startChapterNum: number,
  startChapterVerseReference: string,
  endChapterNum?: number | null,
  endChapterVerseReference?: string | null
) => {
  filteredPassagesStore.update((currentPassages) => {
    // Check if the passage already exists
    const exists = currentPassages.some(
      (p) =>
        p.langCode === langCode &&
        p.bookCode === bookCode &&
        p.startChapter === startChapterNum &&
        p.startChapterVerseRef === startChapterVerseReference &&
        p.endChapter === endChapterNum &&
        p.endChapterVerseRef === endChapterVerseReference
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
        startChapter: startChapterNum,
        startChapterVerseRef: startChapterVerseReference,
        endChapter: endChapterNum,
        endChapterVerseRef: endChapterVerseReference
      }
    ]
  })
}

export const removeBibleReference = (
  langCode: string,
  bookCode: string,
  startChapterNum: number,
  startChapterVerseReference: string,
  endChapterNum?: number | null,
  endChapterVerseReference?: string | null
) => {
  passagesStore.update((currentPassages) => {
    return currentPassages.filter(
      (p) =>
        !(
          p.langCode === langCode &&
          p.bookCode === bookCode &&
          p.startChapter === startChapterNum &&
          p.startChapterVerseRef === startChapterVerseReference &&
          p.endChapter === endChapterNum &&
          p.endChapterVerseRef === endChapterVerseReference
        )
    )
  })
}
