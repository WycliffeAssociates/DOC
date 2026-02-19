<script lang="ts">
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import { langCodesStore } from '$lib/passages/stores/LanguagesStore'
  import { passagesStore } from '$lib/passages/stores/PassagesStore'
  import { passagesWithAvailabilityStore } from '$lib/passages/stores/PassagesWithAvailabilityStore'
  import type { BibleReference } from '$lib/passages/models'
  import { passagesRegExp } from '$lib/passages/utils'
  import BookIcon from '$lib/BookIcon.svelte'
  import EditIcon from '$lib/EditIcon.svelte'
  import CloseIcon from '$lib/CloseIcon.svelte'
  import { bookCodes } from '$lib/bible-books'

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

  $: allPassages = $passagesWithAvailabilityStore || []
  $: sortedPassages = allPassages.slice().sort((a, b) => {
    const pa = a.passage
    const pb = b.passage
    const indexA = bookCodes.indexOf(pa.bookCode)
    const indexB = bookCodes.indexOf(pb.bookCode)
    if (indexA !== indexB) return indexA - indexB
    if (pa.startChapter !== pb.startChapter) return pa.startChapter - pb.startChapter
    const startVerseA = parseInt(pa.startChapterVerseRef, 10)
    const startVerseB = parseInt(pb.startChapterVerseRef, 10)
    if (startVerseA !== startVerseB) return startVerseA - startVerseB
    const endChapterA = pa.endChapter ?? pa.startChapter
    const endChapterB = pb.endChapter ?? pb.startChapter
    if (endChapterA !== endChapterB) return endChapterA - endChapterB
    const endVerseA = parseInt(pa.endChapterVerseRef ?? pa.startChapterVerseRef, 10)
    const endVerseB = parseInt(pb.endChapterVerseRef ?? pb.startChapterVerseRef, 10)
    return endVerseA - endVerseB
  })

  $: shownPassages = sortedPassages?.slice(0, size)
  $: hiddenPassages = sortedPassages?.slice(size)
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

{#if allPassages.length > 0}
  <section id="passages-basket">
    <div data-testid="shown-passages">
      {#each shownPassages as { passage, available }}
        {#if passagesRegExp.test($page.url.pathname)}
          <div
            class="mt-2 flex w-full items-center justify-between
                rounded-lg bg-white p-4 text-xl text-[#66768B]"
            class:text-[#66768B]={available}
            class:text-[#B0B8C3]={!available}
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
            {#if available}
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
    </div>

    {#if hiddenPassages.length > 0}
      <div
        class="collapse collapse-arrow mt-2 w-full rounded-lg
                bg-white text-xl text-[#66768B]"
        data-testid="hidden-passages"
      >
        <input type="checkbox" />
        <div class="collapse-title">
          ({hiddenPassages.length}) items hidden
        </div>
        <div class="collapse-content">
          {#each hiddenPassages as { passage, available }}
            {#if passagesRegExp.test($page.url.pathname)}
              <div
                class="mt-2 flex w-full items-center justify-between
                      rounded-lg bg-white p-2 text-xl text-[#66768B]"
                class:text-[#66768B]={available}
                class:text-[#B0B8C3]={!available}
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
                {#if available}
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
  </section>
{:else}
  <div class="rounded-lg bg-[#e5e8eb] p-6 text-xl text-[#66768b]">
    Selections will appear here once a passage is added
  </div>
{/if}
