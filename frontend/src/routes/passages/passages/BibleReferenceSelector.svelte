<script lang="ts">
  import { passagesStore, addPassageReference } from '$lib/passages/stores/PassagesStore'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguageStore'
  import { onMount } from 'svelte'
  import {
    PUBLIC_CHAPTERS_IN_BOOKS_URL,
    PUBLIC_NT_SURVEY_RG_PASSAGES_URL,
    PUBLIC_STET_PASSAGES_URL
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import type { BibleReference } from './model'

  export let bookCodesAndNames: [string, string][] = []

  let loading = false
  let ntSurveySuccessMessage: string = ''
  let stetSuccessMessage: string = ''
  let passageSuccessMessage: string = ''
  let checkIcon =
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 0A8 8 0 1 0 8 16A8 8 0 0 0 8 0zM3.5 8.5l2.5 2.5L12.5 5l-1-1l-7 7l-2.5-2.5l-1 1z"/></svg>'

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
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getNTSurveyRGPassages(langCode)
      console.log(`bibleReferences[0]: ${bibleReferences[0]}`)
      for (const bibleRef of bibleReferences) {
        addPassageReference(
          langCode,
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
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getSTETPassages(langCode)
      console.log(`bibleReferences[0]: ${bibleReferences[0]}`)
      for (const bibleRef of bibleReferences) {
        addPassageReference(
          langCode,
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

  function handleBookChange(event: Event) {
    const target = event.target as HTMLSelectElement
    selectedBookCode = target.value
    console.log('Book Selected:', selectedBookCode)
    // Manually reset chapter only when book changes, avoiding reactivity loop
    selectedChapter = ''
    chaptersForSelectedBook = chapters[selectedBookCode] || []
    console.log('Chapters for selected book:', chaptersForSelectedBook)
  }

  function handleChapterChange(event: Event) {
    const target = event.target as HTMLSelectElement
    selectedChapter = target.value
    console.log('Chapter selected:', selectedChapter)
  }

  function handleVerseInput(event: Event) {
    const target = event.target as HTMLInputElement
    verseReference = target.value
  }

  let isLoadingNTSurvey = false
  let isLoadingStetPassages = false

  async function handleAddNTSurveyRGPassagesClick() {
    loading = true
    isLoadingNTSurvey = true
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
      isLoadingNTSurvey = false
    }
  }

  function handleNTSurveyCheckboxClick(event: Event) {
    const target = event.target as HTMLInputElement
    if (target.checked) {
      handleAddNTSurveyRGPassagesClick()
    }
  }

  async function handleAddSTETPassagesClick() {
    loading = true
    isLoadingStetPassages = true
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
      isLoadingStetPassages = false
    }
  }

  function handleSTETCheckboxClick(event: Event) {
    const target = event.target as HTMLInputElement
    if (target.checked) {
      handleAddSTETPassagesClick()
    }
  }

  function addPassage() {
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
           border border-[#E5E8EB] p-4
           text-center text-xl text-white
           add-passage-button
           "
      on:click={addPassage}
    >
      Add Passage
    </button>
    <div class="loader-container">
      {#if passageSuccessMessage}
        <div class="success-message text-green-500 ml-2">
          {@html checkIcon}
        </div>
      {/if}
    </div>
  </div>
  <div class="flex h-[56px] items-center mb-2">
    <input
      id="add-nt-survey-passages-checkbox"
      type="checkbox"
      class="checkbox-target checkbox-style"
      on:click={handleNTSurveyCheckboxClick}
    />
    <label
      for="add-nt-survey-passages-checkbox"
      class="pl-1 text-xl text-[#33445C] {isLoadingNTSurvey ? 'text-gray-400' : ''}"
      >Add NT Survey Reviewers' Guide Passages</label
    >
    <div class="loader-container">
      {#if isLoadingNTSurvey}
        <div class="loader"></div>
      {:else if ntSurveySuccessMessage}
        <div class="success-message text-green-500 ml-2">
          {@html checkIcon}
        </div>
      {/if}
    </div>
  </div>
  <div class="flex h-[56px] items-center mb-2">
    <input
      id="add-stet-passages-checkbox"
      type="checkbox"
      class="checkbox-target checkbox-style"
      on:click={handleSTETCheckboxClick}
    />
    <label
      for="add-stet-passages-checkbox"
      class="pl-1 text-xl text-[#33445C] {isLoadingStetPassages ? 'text-gray-400' : ''}"
      >Add STET Passages</label
    >
    <div class="loader-container">
      {#if isLoadingStetPassages}
        <div class="loader"></div>
      {:else if stetSuccessMessage}
        <div class="success-message text-green-500 ml-2">
          {@html checkIcon}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .success-message {
    transition: opacity 1s ease;
    opacity: 1;
  }

  .loader-container {
    display: flex;
    align-items: center;
  }
  .loader {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-top: 4px solid #4caf50;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
    margin-left: 8px;
  }
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
  * :global(.add-passage-button) {
    background:
      linear-gradient(180deg, #1876fd 0%, #015ad9 100%), linear-gradient(0deg, #33445c, #33445c);
  }
  * :global(.add-passage-button:hover) {
    background:
      linear-gradient(180deg, #0765ec 0%, #0149c8 100%), linear-gradient(0deg, #33445c, #33445c);
  }
</style>
