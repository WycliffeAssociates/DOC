<script lang="ts">
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguageStore'
  import { passagesStore } from '$lib/passages/stores/PassagesStore'
  import type { PassageReferenceDto } from '$lib/passages/models'
  import { passagesRegExp } from '$lib/passages/utils'
  import BookIcon from '$lib/BookIcon.svelte'
  import EditIcon from '$lib/EditIcon.svelte'
  import CloseIcon from '$lib/CloseIcon.svelte'

  let size = 5 // Number of passages to show initially

  function uncheckPassage(id: number) {
    $passagesStore = $passagesStore.filter((item: PassageReferenceDto) => item.id != id)
  }

  $: allPassages = $passagesStore || []
  $: shownPassages = allPassages.slice(0, size)
  $: hiddenPassages = allPassages.slice(size)
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
      on:click={() => $langCodeAndNameStore && goto('/passages/passages')}
      disabled={!$langCodeAndNameStore}
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
      >
        <div>
          {#if passage.endChapterNum != null && passage.endChapterNum > 0 && passage.endChapterVerseReference != null}
            <span
              >{passage.bookName}
              {passage.startChapterNum}:{passage.startChapterVerseReference}-{passage.endChapterNum}:{passage.endChapterVerseReference}</span
            >
          {:else}
            <span
              >{passage.bookName}
              {passage.startChapterNum}:{passage.startChapterVerseReference}</span
            >
          {/if}
        </div>
        <button on:click={() => uncheckPassage(passage.id)}>
          <CloseIcon />
        </button>
      </div>
    {:else}
      <div
        class="mt-2 flex w-full items-center justify-between
                rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          {#if passage.endChapterNum != null && passage.endChapterNum > 0 && passage.endChapterVerseReference != null}
            <span
              >{passage.bookName}
              {passage.startChapterNum}:{passage.startChapterVerseReference}-{passage.endChapterNum}:{passage.endChapterVerseReference}</span
            >
          {:else}
            <span
              >{passage.bookName}
              {passage.startChapterNum}:{passage.startChapterVerseReference}</span
            >
          {/if}
        </div>
      </div>
    {/if}
  {/each}

  {#if hiddenPassages.length > 0}
    <div
      class="collapse-arrow collapse mt-2 w-full rounded-lg
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
            >
              <div>
                {#if passage.endChapterNum != null && passage.endChapterNum > 0 && passage.endChapterVerseReference != null}
                  <span
                    >{passage.bookName}
                    {passage.startChapterNum}:{passage.startChapterVerseReference}-{passage.endChapterNum}:{passage.endChapterVerseReference}</span
                  >
                {:else}
                  <span
                    >{passage.bookName}
                    {passage.startChapterNum}:{passage.startChapterVerseReference}</span
                  >
                {/if}
              </div>
              <button on:click={() => uncheckPassage(passage.id)}>
                <span class="ml-2"><CloseIcon /></span>
              </button>
            </div>
          {:else}
            <div
              class="mt-2 flex w-full items-center justify-between
                      rounded-lg bg-white p-2 text-xl text-[#66768B]"
            >
              <div>
                {#if passage.endChapterNum != null && passage.endChapterNum > 0 && passage.endChapterVerseReference != null}
                  <span
                    >{passage.bookName}
                    {passage.startChapterNum}:{passage.startChapterVerseReference}-{passage.endChapterNum}:{passage.endChapterVerseReference}</span
                  >
                {:else}
                  <span
                    >{passage.bookName}
                    {passage.startChapterNum}:{passage.startChapterVerseReference}</span
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
