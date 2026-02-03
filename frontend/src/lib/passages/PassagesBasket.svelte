<script lang="ts">
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import { langCodesStore } from '$lib/passages/stores/LanguagesStore'
  import { passagesStore } from '$lib/passages/stores/PassagesStore'
  import type { BibleReference } from '$lib/passages/models'
  import { isAvailable, passagesRegExp } from '$lib/passages/utils'
  import BookIcon from '$lib/BookIcon.svelte'
  import EditIcon from '$lib/EditIcon.svelte'
  import CloseIcon from '$lib/CloseIcon.svelte'
  import { bookCodes } from '$lib/bible-books'
  import { availablePassagesStore } from '$lib/passages/stores/PassagesStore'

  let size = 5 // Number of passages to show initially

  function uncheckPassage(passage: BibleReference) {
    $passagesStore = $passagesStore.filter(
      (item: BibleReference) =>
        item.langCode !== passage.langCode ||
        item.bookCode !== passage.bookCode ||
        item.startChapter !== passage.startChapter ||
        item.startChapterVerseRef !== passage.startChapterVerseRef ||
        item.endChapter !== passage.endChapter ||
        item.endChapterVerseRef !== passage.endChapterVerseRef
    )
  }

  $: allPassages = $passagesStore || []
  $: sortedPassages = allPassages?.slice().sort((a: BibleReference, b: BibleReference) => {
    const indexA = bookCodes.indexOf(a.bookCode)
    const indexB = bookCodes.indexOf(b.bookCode)
    if (indexA !== indexB) return indexA - indexB
    // Compare startChapter
    if (a.startChapter !== b.startChapter) return a.startChapter - b.startChapter
    // Compare start chapter's verse ref
    const startVerseA = parseInt(a.startChapterVerseRef, 10)
    const startVerseB = parseInt(b.startChapterVerseRef, 10)
    if (startVerseA !== startVerseB) return startVerseA - startVerseB
    // Compare endChapter (if present, otherwise use startChapter)
    const endChapterA = a.endChapter ?? a.startChapter
    const endChapterB = b.endChapter ?? b.startChapter
    if (endChapterA !== endChapterB) return endChapterA - endChapterB
    // Compare end chapter's verse ref (if present, otherwise use startChapterVerseRef)
    const endVerseA = parseInt(a.endChapterVerseRef ?? a.startChapterVerseRef, 10)
    const endVerseB = parseInt(b.endChapterVerseRef ?? b.startChapterVerseRef, 10)
    return endVerseA - endVerseB
  })

  $: shownPassages = sortedPassages?.slice(0, size)
  $: hiddenPassages = sortedPassages?.slice(size)

  // Set reactivity for available passages so that basket stays up to date
  $: availablePassages = $availablePassagesStore
</script>

{#if passagesRegExp.test($page.url.pathname)}
  <div class="my-2 flex items-center">
    <BookIcon />
    <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Passages</h2>
  </div>
{:else}
  <div class="my-2 flex items-center justify-between">
    <div class="flex items-center justify-between">
      <BookIcon />
      <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Passages</h2>
    </div>
    <button
      class="flex rounded bg-white px-4 py-2 text-xl text-[#33445c] hover:bg-[#efefef]"
      on:click={() => $langCodesStore && goto('/passages/passages')}
      disabled={!$langCodesStore}
    >
      <EditIcon />
      <span class="ml-2"> Edit </span>
    </button>
  </div>
{/if}

{#if $passagesStore && $passagesStore.length > 0}
  {#each shownPassages as passage}
    {#if passagesRegExp.test($page.url.pathname)}
      <div
        class="mt-2 flex w-full items-center justify-between
                rounded-lg bg-white p-4 text-xl text-[#66768B]"
        class:text-[#66768B]={isAvailable(passage, availablePassages)}
        class:text-[#B0B8C3]={!isAvailable(passage, availablePassages)}
      >
        <div>
          {#if passage.endChapter && passage.endChapter > 0 && passage.endChapterVerseRef}
            <span
              >{passage.bookName}
              {passage.startChapter}:{passage.startChapterVerseRef}-{passage.endChapter}:{passage.endChapterVerseRef}
              ({passage.langCode})</span
            >
          {:else}
            <span
              >{passage.bookName}
              {passage.startChapter}:{passage.startChapterVerseRef}
              ({passage.langCode})</span
            >
          {/if}
        </div>
        {#if isAvailable(passage, availablePassages)}
          <button on:click={() => uncheckPassage(passage)}>
            <CloseIcon />
          </button>
        {/if}
      </div>
    {:else}
      <div
        class="mt-2 flex w-full items-center justify-between
                rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          {#if passage.endChapter && passage.endChapter > 0 && passage.endChapterVerseRef}
            ({passage.langCode})
            <span
              >{passage.bookName}
              {passage.startChapter}:{passage.startChapterVerseRef}-{passage.endChapter}:{passage.endChapterVerseRef}
              ({passage.langCode})</span
            >
          {:else}
            <span
              >{passage.bookName}
              {passage.startChapter}:{passage.startChapterVerseRef} ({passage.langCode})</span
            >
          {/if}
        </div>
      </div>
    {/if}
  {/each}

  {#if hiddenPassages.length > 0}
    <div
      class="collapse collapse-arrow mt-2 w-full rounded-lg
                bg-white text-xl text-[#66768B]"
    >
      <input type="checkbox" />
      <div class="collapse-title">
        ({hiddenPassages.length}) items hidden
      </div>
      <div class="collapse-content">
        {#each hiddenPassages as passage}
          {#if passagesRegExp.test($page.url.pathname)}
            <div
              class="mt-2 flex w-full items-center justify-between
                      rounded-lg bg-white p-2 text-xl text-[#66768B]"
              class:text-[#66768B]={isAvailable(passage, availablePassages)}
              class:text-[#B0B8C3]={!isAvailable(passage, availablePassages)}
            >
              <div>
                {#if passage.endChapter && passage.endChapter > 0 && passage.endChapterVerseRef}
                  <span
                    >{passage.bookName}
                    {passage.startChapter}:{passage.startChapterVerseRef}-{passage.endChapter}:{passage.endChapterVerseRef}
                    ({passage.langCode})</span
                  >
                {:else}
                  <span
                    >{passage.bookName}
                    {passage.startChapter}:{passage.startChapterVerseRef} ({passage.langCode})</span
                  >
                {/if}
              </div>
              {#if isAvailable(passage, availablePassages)}
                <button on:click={() => uncheckPassage(passage)}>
                  <CloseIcon />
                </button>
              {/if}
            </div>
          {:else}
            <div
              class="mt-2 flex w-full items-center justify-between
                      rounded-lg bg-white p-2 text-xl text-[#66768B]"
            >
              <div>
                {#if passage.endChapter && passage.endChapter > 0 && passage.endChapterVerseRef}
                  ({passage.langCode})
                  <span
                    >{passage.bookName}
                    {passage.startChapter}:{passage.startChapterVerseRef}-{passage.endChapter}:{passage.endChapterVerseRef}
                    ({passage.langCode})</span
                  >
                {:else}
                  <span
                    >{passage.bookName}
                    {passage.startChapter}:{passage.startChapterVerseRef} ({passage.langCode})</span
                  >
                {/if}
              </div>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  {/if}
{:else}
  <div class="rounded-lg bg-[#e5e8eb] p-6 text-xl text-[#66768b]">
    Selections will appear here once a passage is added
  </div>
{/if}
