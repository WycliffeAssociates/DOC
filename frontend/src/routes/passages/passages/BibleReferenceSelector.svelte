<script lang="ts">
  import { passagesStore, addPassageReference } from '$lib/passages/stores/PassagesStore'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguageStore'
  import { onMount } from 'svelte'
  import {
    PUBLIC_CHAPTERS_IN_BOOKS_URL,
    PUBLIC_NT_SURVEY_RG_PASSAGES_URL,
    PUBLIC_STET_PASSAGES_URL,
    PUBLIC_TAILWIND_SM_MIN_WIDTH
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import type { BibleReference } from './model'

  export let bookCodesAndNames: [string, string][] = []

  let loading = false
  let ntSurveySuccessMessage: string = ''
  let stetSuccessMessage: string = ''
  let passageSuccessMessage: string = ''

  let selectedBookCode: string = ''
  let selectedChapter: string = ''
  let verseReference: string = ''
  let chaptersForSelectedBook: number[] = []
  let chapters: Record<string, number[]> = {}


  onMount(() => {
    getChaptersInBooks()
      .then((chaptersInBooks_) => {
        chapters = { ...chaptersInBooks_ } // Ensure reactivity with {...blah}
      })
      .catch((err) => console.error(err))
  })

  async function getChaptersInBooks(
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    chaptersInBooksUrl = <string>PUBLIC_CHAPTERS_IN_BOOKS_URL
  ): Promise<Record<string, number[]>> {
    const response = await fetch(`${apiRootUrl}${chaptersInBooksUrl}`)
    const chaptersInBooks: Record<string, number[]> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return chaptersInBooks
  }


  async function getNTSurveyRGPassages(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    ntSurveyRgPassagesUrl = <string>PUBLIC_NT_SURVEY_RG_PASSAGES_URL
  ): Promise<Array<BibleReference>> {
    const url = `${apiRootUrl}${ntSurveyRgPassagesUrl}/${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bibleReferences: Array<BibleReference> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bibleReferences
  }

  export async function addNTSurveyRGPassages() {
    try {
      const bibleReferences = await getNTSurveyRGPassages($langCodeAndNameStore.split(',')[0])
      console.log(`bibleReferences[0]: ${bibleReferences[0]}`)
      for (const bibleRef of bibleReferences) {
        addPassageReference(
          $langCodeAndNameStore.split(',')[0],
          bibleRef.book_code,
          bibleRef.book_name,
          Number(bibleRef.start_chapter),
          bibleRef.start_chapter_verse_ref,
          Number(bibleRef.end_chapter),
          bibleRef.end_chapter_verse_ref
        )
      }
    } catch (error) {
      console.error('Failed to add NT Survey RG passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }

  async function getSTETPassages(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    stetPassagesUrl = <string>PUBLIC_STET_PASSAGES_URL
  ): Promise<Array<BibleReference>> {
    const url = `${apiRootUrl}${stetPassagesUrl}/${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bibleReferences: Array<BibleReference> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bibleReferences
  }

  export async function addSTETPassages() {
    try {
      const bibleReferences = await getSTETPassages($langCodeAndNameStore.split(',')[0])
      console.log(`bibleReferences[0]: ${bibleReferences[0]}`)
      for (const bibleRef of bibleReferences) {
        addPassageReference(
          $langCodeAndNameStore.split(',')[0],
          bibleRef.book_code,
          bibleRef.book_name,
          Number(bibleRef.start_chapter),
          bibleRef.start_chapter_verse_ref,
          Number(bibleRef.end_chapter),
          bibleRef.end_chapter_verse_ref
        )
      }
    } catch (error) {
      console.error('Failed to add STET passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }


  const handleBookChange = (event: Event) => {
    const target = event.target as HTMLSelectElement
    selectedBookCode = target.value
    console.log('Book Selected:', selectedBookCode)
    // Manually reset chapter only when book changes, avoiding reactivity loop
    selectedChapter = ''
    chaptersForSelectedBook = chapters[selectedBookCode] || []
    console.log('Chapters for selected book:', chaptersForSelectedBook)
  }

  const handleChapterChange = (event: Event) => {
    const target = event.target as HTMLSelectElement
    selectedChapter = target.value
    console.log('Chapter selected:', selectedChapter)
  }

  const handleVerseInput = (event: Event) => {
    const target = event.target as HTMLInputElement
    verseReference = target.value
  }


  async function handleAddNTSurveyRGPassagesClick() {
    loading = true
    try {
      await addNTSurveyRGPassages()
      ntSurveySuccessMessage = '✔'
      setTimeout(() => {
        ntSurveySuccessMessage = ''
      }, 4000)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      loading = false
    }
  }

  async function handleAddSTETPassagesClick() {
    loading = true
    try {
      await addSTETPassages()
      stetSuccessMessage = '✔'
      setTimeout(() => {
        stetSuccessMessage = ''
      }, 4000)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      loading = false
    }
  }


  const addPassage = () => {
    if (selectedBookCode && selectedChapter && verseReference) {
      const bookName =
        bookCodesAndNames.find(([code]) => code === selectedBookCode)?.[1] ?? 'Unknown'
      addPassageReference(
        $langCodeAndNameStore.split(',')[0],
        selectedBookCode,
        bookName,
        Number(selectedChapter),
        verseReference,
        null,
        null
      )
      passageSuccessMessage = '✔'
      setTimeout(() => {
        passageSuccessMessage = ''
      }, 4000)
      selectedBookCode = ''
      selectedChapter = ''
      verseReference = ''
    }
  }

</script>

<div class="flex flex-col">
  <div class="flex items-center">
    <div class="mr-2">
      <label for="book" class="block text-sm font-medium text-gray-700">Bible Book</label>
      <select
        id="book"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        on:change={handleBookChange}
        bind:value={selectedBookCode}
      >
        <option value="" disabled selected>Choose a book</option>
        {#each bookCodesAndNames as [code, name]}
          <option value={code}>{name}</option>
        {/each}
      </select>
    </div>
    <div class="mr-2">
      <label for="chapter" class="block text-sm font-medium text-gray-700">Chapter</label>
      <select
        id="chapter"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        on:change={handleChapterChange}
        value={selectedChapter}
        disabled={!selectedBookCode || !chaptersForSelectedBook.length}
      >
        <option value="" disabled selected>Choose a chapter</option>
        {#each chaptersForSelectedBook as chapter}
          <option value={String(chapter)} selected={String(chapter) === selectedChapter}>
            {chapter}
          </option>
        {/each}
      </select>
    </div>
    <div class="mr-2">
      <label for="verses" class="block text-sm font-medium text-gray-700">Verse(s)</label>
      <input
        id="verses"
        type="text"
        placeholder="e.g., 1,2,5-7,20"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        on:input={handleVerseInput}
        bind:value={verseReference}
      />
    </div>
    <button
      type="button"
      class="mt-4 ml-2 w-1/2 rounded-md
           border border-[#E5E8EB] bg-[#F2F3F5] p-4
           text-center text-xl text-[#B3B9C2] hover:bg-[#efefef]"
      on:click={addPassage}
    >
      Add Passage
    </button>
  </div>
  <div class="flex h-[56px] items-center mb-2">
    <input
      id="add-nt-survey-passages-checkbox"
      type="checkbox"
      class="checkbox-target checkbox-style"
      on:click={handleAddNTSurveyRGPassagesClick}
    />
    <label for="add-nt-survey-passages-checkbox" class="pl-1 text-xl text-[#33445C]"
      >Add NT Survey Reviewers' Guide Passages</label
    >
    {#if ntSurveySuccessMessage}
      <div class="success-message text-green-500 ml-2">
        {ntSurveySuccessMessage}
      </div>
    {/if}
  </div>
  <div class="flex h-[56px] items-center mb-2">
    <input
      id="add-stet-passages-checkbox"
      type="checkbox"
      class="checkbox-target checkbox-style"
      on:click={handleAddSTETPassagesClick}
    />
    <label for="add-stet-passages-checkbox" class="pl-1 text-xl text-[#33445C]"
      >Add STET Passages</label
    >
    {#if stetSuccessMessage}
      <div class="success-message text-green-500 ml-2">
        {stetSuccessMessage}
      </div>
    {/if}
  </div>
</div>

<style>
  .success-message {
    transition: opacity 1s ease;
    opacity: 1;
  }
</style>
