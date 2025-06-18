<script lang="ts">
  import { passagesStore, addPassageReference } from '$lib/passages/stores/PassagesStore'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguageStore'

  export let bookCodesAndNames: [string, string][] = []
  export let selectedBookCode: string = ''
  export let selectedChapter: string = ''
  export let verseReference: string = ''
  export let chaptersForSelectedBook: number[] = []

  export let handleBookChange: (event: Event) => void
  export let handleChapterChange: (event: Event) => void
  export let handleVerseInput: (event: Event) => void
  export let addNTSurveyRGPassages: () => Promise<void>
  export let addSTETPassages: () => Promise<void>

  let loading = false
  let ntSurveySuccessMessage: string = ''
  let stetSuccessMessage: string = ''
  let passageSuccessMessage: string = ''

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
