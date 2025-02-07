<script lang="ts">
  import { onMount } from 'svelte'
  import otBooks from '$lib/ot-books'
  import { ntBookStore, otBookStore, bookCountStore } from '$lib/passages/stores/BooksStore'
  import {
    PUBLIC_BOOK_CODES_FROM_USFM_ONLY_URL,
    PUBLIC_CHAPTERS_IN_BOOKS_URL,
    PUBLIC_PASSAGES_URL,
    PUBLIC_TAILWIND_SM_MIN_WIDTH
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'
  import Modal from '$lib/Modal.svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import WizardBreadcrumb from '$lib/passages/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/passages/WizardBasket.svelte'
  import { langCodeAndNameStore, langCountStore } from '$lib/passages/stores/LanguageStore'
  import { passagesStore, addPassageReference } from '$lib/passages/stores/PassagesStore'

  // For use by Mobile UI
  let showWizardBasketModal = false

  async function getBookCodesAndNames(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    bookCodesUrl = <string>PUBLIC_BOOK_CODES_FROM_USFM_ONLY_URL
  ): Promise<Array<[string, string]>> {
    const url = `${apiRootUrl}${bookCodesUrl}${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bookCodesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bookCodesAndNames
  }

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

  // Resolve promise for data reactively
  let bookCodesAndNames: Array<[string, string]> = []
  let chapters: Record<string, number[]> = {}

  onMount(() => {
    let langCode = $langCodeAndNameStore.split(',')[0]
    console.log(langCode)
    console.log(`langCode: ${JSON.stringify(langCode)}`)
    getBookCodesAndNames(langCode)
      .then((bookCodesAndNames_) => {
        bookCodesAndNames = [...bookCodesAndNames_] // Ensure reactivity with [...blah]
      })
      .catch((err) => console.error(err))

    getChaptersInBooks()
      .then((chaptersInBooks_) => {
        chapters = { ...chaptersInBooks_ } // Ensure reactivity with [...blah]
      })
      .catch((err) => console.error(err))
  })

  let selectedBookCode: string = ''
  let selectedChapter: string = ''
  let verseReference: string = ''
  let chaptersForSelectedBook: number[] = []

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

  const addPassage = () => {
    if (selectedBookCode && selectedChapter && verseReference) {
      const bookName = bookCodesAndNames.find(([code]) => code === selectedBookCode)?.[1] ?? "Unknown";
      addPassageReference(
        $langCodeAndNameStore.split(",")[0],
        selectedBookCode,
        bookName,
        Number(selectedChapter),
        verseReference
      )

      // Reset fields for the next entry
      selectedBookCode = ''
      selectedChapter = ''
      verseReference = ''
    }
  }

  let windowWidth: number
  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number

  $: console.log(`windowWidth: ${windowWidth}`)
  $: console.log(`selectedBookCode: ${selectedBookCode}`)
  $: console.log(`selectedChapter: ${selectedChapter}`)
  $: console.log(`verseReference: ${verseReference}`)
  // $: console.log(`chapters: ${JSON.stringify(chapters)}`)
  // $: console.log(`bookCodesAndNames: ${JSON.stringify(bookCodesAndNames)}`)
  // $: console.log(`typeof bookCodesAndNames: ${typeof bookCodesAndNames}`)
  $: console.log(`$passagesStore: ${JSON.stringify($passagesStore)}`)
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <!-- center -->
  <div class="flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="ml-4 text-4xl font-normal leading-[48px] text-[#33445C]">Add passages</h3>
    <div class="ml-4 mt-2 flex items-center bg-white px-2 py-2">
      {#if !bookCodesAndNames}
        <div class="ml-4">
          <ProgressIndicator />
        </div>
      {:else}
        <div class="flex items-center">
          <!-- Bible Book Dropdown -->
          <div>
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

          <!-- Chapter Dropdown -->
          <div>
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

          <!-- Verse Reference Input -->
          <div>
            <label for="verses" class="block text-sm font-medium text-gray-700">Verse(s)</label>
            <input
              id="verses"
              type="text"
              placeholder="e.g., 1,2,5-7"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              on:input={handleVerseInput}
              bind:value={verseReference}
            />
          </div>

          <!-- Add Passage Button -->
          <button
            type="button"
            class="mb-4 mt-2 w-1/2 rounded-md
                    border border-[#E5E8EB] bg-[#F2F3F5] p-4
                    text-center text-xl text-[#B3B9C2] hover:bg-[#efefef]"
            on:click={addPassage}
          >
            Add Passage
          </button>
        </div>
      {/if}
    </div>
  </div>

  <!-- if isMobile -->
  {#if showWizardBasketModal}
    <WizardBasketModal title="Your selections" bind:showWizardBasketModal>
      <svelte:fragment slot="body">
        <WizardBasket />
      </svelte:fragment>
    </WizardBasketModal>
  {/if}
  <!-- else -->
  <div class="hidden sm:flex sm:w-1/3">
    <WizardBasket />
  </div>
</div>

<style global lang="postcss">
  #filter-gl-langs,
  #filter-non-gl-langs {
    text-indent: 17px;
    padding-left: 5px;
    margin-right: 5px;
    background-image: url('data:image/svg+xml,<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M15.5014 14.0014H14.7114L14.4314 13.7314C15.0564 13.0054 15.5131 12.1502 15.769 11.2271C16.0248 10.3039 16.0735 9.33559 15.9114 8.39144C15.4414 5.61144 13.1214 3.39144 10.3214 3.05144C9.33706 2.92691 8.33723 3.02921 7.39846 3.35053C6.4597 3.67185 5.60688 4.20366 4.90527 4.90527C4.20366 5.60688 3.67185 6.4597 3.35053 7.39846C3.02921 8.33723 2.92691 9.33706 3.05144 10.3214C3.39144 13.1214 5.61144 15.4414 8.39144 15.9114C9.33559 16.0735 10.3039 16.0248 11.2271 15.769C12.1502 15.5131 13.0054 15.0564 13.7314 14.4314L14.0014 14.7114V15.5014L18.2514 19.7514C18.6614 20.1614 19.3314 20.1614 19.7414 19.7514C20.1514 19.3414 20.1514 18.6714 19.7414 18.2614L15.5014 14.0014ZM9.50144 14.0014C7.01144 14.0014 5.00144 11.9914 5.00144 9.50144C5.00144 7.01144 7.01144 5.00144 9.50144 5.00144C11.9914 5.00144 14.0014 7.01144 14.0014 9.50144C14.0014 11.9914 11.9914 14.0014 9.50144 14.0014Z" fill="%2366768B"/></svg>');
    background-repeat: no-repeat;
    background-position: left center;
    outline: 0;
  }
  div.target:has(input[type='checkbox']:checked) {
    background: #e6eefb;
  }
  div.target:has(input[type='radio']:checked) {
    background: #e6eefb;
  }
  div.radio-target:has(input[type='radio']:checked) {
    background: #e6eefb;
  }
  .radio-style {
    @apply h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600;
  }
  .search-style {
    @apply h-full w-full rounded-[7px] border border-gray-200 bg-transparent px-3 py-2.5 font-sans text-xl  font-normal text-[#33445c] outline outline-0 transition-all focus:border-2 focus:border-gray-900 focus:outline-0;
  }
</style>
