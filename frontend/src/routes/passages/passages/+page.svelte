<script lang="ts">
  import type { PassageReferenceDto } from '$lib/passages/models'
  import BibleReferenceSelector from './BibleReferenceSelector.svelte'
  import { onMount } from 'svelte'
  import {
    PUBLIC_BOOK_CODES_FROM_USFM_ONLY_URL,
    PUBLIC_CHAPTERS_IN_BOOKS_URL,
    PUBLIC_NT_SURVEY_RG_PASSAGES_URL,
    PUBLIC_TAILWIND_SM_MIN_WIDTH
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import Modal from '$lib/Modal.svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import WizardBreadcrumb from '$lib/passages/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/passages/WizardBasket.svelte'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguageStore'
  import { passagesStore, addPassageReference } from '$lib/passages/stores/PassagesStore'
  import type { BibleReference } from "./model"

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
        chapters = { ...chaptersInBooks_ } // Ensure reactivity with {...blah}
      })
      .catch((err) => console.error(err))
  })

  function removePassage(id: number) {
    $passagesStore = $passagesStore.filter((item: PassageReferenceDto) => item.id != id)
  }

  $: if (bookCodesAndNames && bookCodesAndNames.length > 0) {
    for (let passageReferenceDto of $passagesStore) {
      if (!bookCodesAndNames.map(([bookCode]) => bookCode).includes(passageReferenceDto.bookCode)) {
        removePassage(passageReferenceDto.id)
      }
    }
  }

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
      const bookName =
        bookCodesAndNames.find(([code]) => code === selectedBookCode)?.[1] ?? 'Unknown'
      addPassageReference(
        $langCodeAndNameStore.split(',')[0],
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

  async function getBibleReferences(
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
      const bibleReferences = await getBibleReferences($langCodeAndNameStore.split(",")[0])
      console.log(`bibleReferences[0]: ${bibleReferences[0]}`)
      for (const bibleRef of bibleReferences) {
          addPassageReference(
            $langCodeAndNameStore.split(",")[0],
            bibleRef.book_code,
            bibleRef.book_name,
            Number(bibleRef.chapter),
            bibleRef.verse_ref
          )
      }
    } catch (error) {
      console.error("Failed to add NT Survey RG passages:", error)
    } finally {
      console.log("Passages added successfully")
    }
  }

  let windowWidth: number = typeof window !== "undefined" ? window.innerWidth : 0
  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number

  $: console.log(`windowWidth: ${windowWidth}`)
  $: console.log(`selectedBookCode: ${selectedBookCode}`)
  $: console.log(`selectedChapter: ${selectedChapter}`)
  $: console.log(`verseReference: ${verseReference}`)
  $: console.log(`$passagesStore: ${JSON.stringify($passagesStore)}`)
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <!-- center -->
  <div class="flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="ml-4 text-4xl font-normal leading-[48px] text-[#33445C]">Add Passages</h3>
    <div class="ml-4 mt-2 flex items-center bg-white px-2 py-2">
      {#if !bookCodesAndNames || bookCodesAndNames.length === 0}
        <div class="ml-4">
          <ProgressIndicator
            labelString="Analyzing books available for language chosen, please be patient..."
          />
        </div>
      {:else}
        <BibleReferenceSelector
          {bookCodesAndNames}
          bind:selectedBookCode
          bind:selectedChapter
          bind:verseReference
          {chaptersForSelectedBook}
          {handleBookChange}
          {handleChapterChange}
          {handleVerseInput}
          {addPassage}
          {addNTSurveyRGPassages}
        />
        {#if windowWidth < TAILWIND_SM_MIN_WIDTH}
          <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
            <div class="relative">
              <svg
                width="56"
                height="48"
                viewBox="0 0 56 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z"
                  fill="#33445C"
                />
                <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB" />
              </svg>
              {#if $passagesStore.length > 0}
                <!-- badge -->
                <div
                  class="bg-neutral-focus absolute -right-0.5 -top-0.5
                           h-7 w-7
                           rounded-full
                           text-center text-xl text-[#33445C]"
                  style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                >
                  <span
                    class="text-[8px]
                                   text-white">{$passagesStore.length}</span
                  >
                </div>
              {/if}
            </div>
          </button>
        {/if}
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
