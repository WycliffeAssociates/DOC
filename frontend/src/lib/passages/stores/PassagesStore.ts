import { writable } from 'svelte/store'
import type { PassageReferenceDto } from '../models/passage'

// Define the passages store
export const passagesStore = writable<PassageReferenceDto[]>([])

// Define the addPassage method
export const addPassageReference = (
  langCode: string,
  bookCode: string,
  bookName: string,
  chapterNum: number,
  verseReference: string
) => {
  passagesStore.update((currentPassages) => [
    ...currentPassages,
    {
      id: Math.max(0, ...currentPassages.map((p) => p.id)) + 1,
      langCode,
      bookCode,
      bookName,
      chapterNum,
      verseReference
    }
  ])
}
