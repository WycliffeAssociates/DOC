<script lang="ts">
  import { addBibleReference, addAvailableBibleReference } from '$lib/passages/stores/PassagesStore'
  import { langCodesStore, langCountStore } from '$lib/passages/stores/LanguagesStore'
  import type { BibleReference } from '$lib/passages/models'

  export let chapters: Record<string, number[]>
  export let checkIcon: string
  export let bookCodesAndNamesLang0: [string, string][]
  export let bookCodesAndNamesLang1: [string, string][]
  let selectedBookCode: string = ''
  let selectedChapter: string = ''
  let chaptersForSelectedBook: number[] = []
  let verseReference: string = ''
  let buttonEnabled = false
  let passageSuccessMessage: string = ''

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

  function addPassage() {
    if (selectedBookCode && selectedChapter && verseReference) {
      const bookEntry = bookCodesAndNamesLang0.find(([code]) => code === selectedBookCode)
      const bookName = bookEntry ? bookEntry[1] : 'Unknown'
      const bibleRefLang0: BibleReference = {
        langCode: $langCodesStore[0],
        bookCode: selectedBookCode,
        bookName: bookName,
        startChapter: Number(selectedChapter),
        startChapterVerseRef: verseReference,
        endChapter: null,
        endChapterVerseRef: null
      }
      addBibleReference(bibleRefLang0)
      addAvailableBibleReference(bibleRefLang0)
      if ($langCountStore > 1) {
        const bibleRefLang1 = {
          langCode: $langCodesStore[1],
          bookCode: selectedBookCode,
          bookName: bookName,
          startChapter: Number(selectedChapter),
          startChapterVerseRef: verseReference,
          endChapter: null,
          endChapterVerseRef: null
        }
        addBibleReference(bibleRefLang1)
        addAvailableBibleReference(bibleRefLang1)
      }
      passageSuccessMessage = '✔'
      setTimeout(() => {
        passageSuccessMessage = ''
        // Reset the button and fields
        selectedBookCode = ''
        selectedChapter = ''
        verseReference = ''
        buttonEnabled = false // Change button state back to disabled
      }, 4000)
      selectedBookCode = ''
      selectedChapter = ''
      verseReference = ''
    }
  }

  // Watcher for input fields to update button state
  $: buttonEnabled = Boolean(selectedBookCode && selectedChapter && verseReference)
</script>

<div class="ml-2 mt-4 block text-xl font-bold text-[#33445C]">Other Passages</div>
<div id="add-other-passages" class="ml-2 flex items-center">
  <div class="mr-2">
    <label for="book" class="block text-sm font-medium text-gray-700">Bible Book</label>
    <select
      id="book"
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
      on:change={handleBookChange}
      bind:value={selectedBookCode}
    >
      <option value="" disabled selected>Choose a book</option>
      {#each bookCodesAndNamesLang0 as [code, name]}
        <option value={code}>{name}</option>
      {/each}
      {#each bookCodesAndNamesLang1 as [code2, name2]}
        <option value={code2}>{name2}</option>
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
      class="mt-1 block w-full rounded-md border-2 border-blue-500 shadow-sm focus:border-indigo-600 focus:ring focus:ring-indigo-200 sm:text-sm"
      on:input={handleVerseInput}
      bind:value={verseReference}
    />
  </div>
  <button
    type="button"
    class={`ml-2 mt-4 w-1/2 rounded-md
           border border-[#E5E8EB] p-4
           text-center text-xl text-white
           ${buttonEnabled ? 'add-passage-button' : 'add-passage-button-disabled'} `}
    on:click={addPassage}
    disabled={!buttonEnabled}
  >
    Add Passage
  </button>
  <div class="loader-container">
    {#if passageSuccessMessage}
      <div class="success-message ml-2 text-green-500">
        {@html checkIcon}
      </div>
    {/if}
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
  *:global(.add-passage-button-disabled) {
    background:
      linear-gradient(180deg, #a3c1ff 0%, #8bb3ff 100%),
      /* lighter blue */ linear-gradient(0deg, #33447e, #33447e);
  }
  * :global(.add-passage-button-disabled:hover) {
    background:
      linear-gradient(180deg, #cce4ff 0%, #a3c1ff 100%), linear-gradient(0deg, #33447e, #33447e);
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
