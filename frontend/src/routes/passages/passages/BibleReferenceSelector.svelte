<script lang="ts">
  export let bookCodesAndNames: [string, string][] = []
  export let selectedBookCode: string = ''
  export let selectedChapter: string = ''
  export let verseReference: string = ''
  export let chaptersForSelectedBook: number[] = []

  export let handleBookChange: (event: Event) => void
  export let handleChapterChange: (event: Event) => void
  export let handleVerseInput: (event: Event) => void
  export let addPassage: () => void
</script>

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
  <div class="ml-2">
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
  <div class="ml-2">
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
    class="mt-4 ml-2 w-1/2 rounded-md
           border border-[#E5E8EB] bg-[#F2F3F5] p-4
           text-center text-xl text-[#B3B9C2] hover:bg-[#efefef]"
    on:click={addPassage}
  >
    Add Passage
  </button>
</div>
