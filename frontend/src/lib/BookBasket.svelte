<script lang="ts">
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import { bookRegExp, getCode, getName } from '$lib/utils'
  import { langCountStore } from '$lib/stores/LanguagesStore'
  import { bookCountStore, ntBookStore, otBookStore } from '$lib/stores/BooksStore'
  import BookIcon from '$lib/BookIcon.svelte'
  import EditIcon from '$lib/EditIcon.svelte'
  import CloseIcon from '$lib/CloseIcon.svelte'
  import GlobeIcon from '$lib/GlobeIcon.svelte'

  function uncheckBook(bookCodeAndName: string) {
    $otBookStore = $otBookStore.filter((item) => item != bookCodeAndName)
    $ntBookStore = $ntBookStore.filter((item) => item != bookCodeAndName)
  }

  $: {
    if ($langCountStore === 0) {
      $otBookStore = []
      $ntBookStore = []
      $bookCountStore = 0
    }
  }
  // Slice the collection of books into the first 'size' amount and
  // the remainder so that the UI can display size + 1 to end of
  // collection amount of books in a collapse control.
  let size = 5
  $: allBooks = [...$otBookStore, ...$ntBookStore]
  $: shownBooks = allBooks.slice(0, size)
  $: hiddenBooks = allBooks.slice(size, -1)
</script>

{#if !bookRegExp.test($page.url.pathname) && $bookCountStore > 0}
  <div class="my-2 flex items-center justify-between">
    <div class="flex items-center justify-between">
      <BookIcon />
      <h2 class="ml-2 text-xl text-xl font-semibold text-[#33445C]">Book</h2>
    </div>
    <button
      class="flex rounded bg-white px-4 py-2 text-xl text-[#33445c] hover:bg-[#efefef]"
      on:click={() => goto('/books')}
    >
      <EditIcon />
      <span class="ml-2"> Edit </span>
    </button>
  </div>
{:else}
  <div class="my-2 flex items-center">
    <BookIcon />
    <h2 class="ml-2 text-xl text-xl font-semibold text-[#33445C]">Book</h2>
  </div>
{/if}
{#if $bookCountStore > 0}
  {#each shownBooks as bookCodeAndName}
    {#if bookRegExp.test($page.url.pathname)}
      <div
        class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          <span>{getName(bookCodeAndName)}</span><span class="ml-2"
            >({getCode(bookCodeAndName)})</span
          >
        </div>
        <button on:click={() => uncheckBook(bookCodeAndName)}>
          <CloseIcon />
        </button>
      </div>
    {:else}
      <div
        class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          <span>{getName(bookCodeAndName)}</span><span class="ml-2"
            >({getCode(bookCodeAndName)})</span
          >
        </div>
      </div>
    {/if}
  {/each}
  <!-- Put remainder books in a collapsed accordion that can be expanded -->
  {#if hiddenBooks.length > 0}
    <div
      class="collapse-arrow collapse mt-2 w-full rounded-lg
                  bg-white text-xl text-[#66768B]"
    >
      <input type="checkbox" />
      <div class="collapse-title">
        ({hiddenBooks.length}) items hidden
      </div>
      <div class="collapse-content">
        {#each hiddenBooks as bookCodeAndName}
          {#if bookRegExp.test($page.url.pathname)}
            <div
              class="mt-2 flex w-full items-center
                       justify-between rounded-lg bg-white p-2 text-xl text-[#66768B]"
            >
              <div>
                <span>{getName(bookCodeAndName)}</span><span class="ml-2"
                  >({getCode(bookCodeAndName)})</span
                >
              </div>
              <button on:click={() => uncheckBook(bookCodeAndName)}>
                <GlobeIcon />
              </button>
            </div>
          {:else}
            <div
              class="mt-2 flex w-full items-center
                       justify-between rounded-lg bg-white p-2 text-xl text-[#66768B]"
            >
              <div>
                <span>{getName(bookCodeAndName)}</span><span class="ml-2"
                  >({getCode(bookCodeAndName)})</span
                >
              </div>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  {/if}
{:else}
  <div class="rounded-lg bg-[#e5e8eb] p-6 text-xl text-[#66768B]">
    Selections will appear here once a book is selected
  </div>
{/if}
