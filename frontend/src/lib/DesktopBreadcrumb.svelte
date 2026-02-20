<script lang="ts">
  import { PUBLIC_MAX_LANGUAGES } from '$env/static/public'
  import { page } from '$app/stores'
  import BackButton from './BackButton.svelte'
  import NextButton from './NextButton.svelte'
  import { langCountStore } from '$lib/stores/LanguagesStore'
  import { bookCountStore } from '$lib/stores/BooksStore'
  import { resourceTypesCountStore } from '$lib/stores/ResourceTypesStore'
  import { langRegExp, bookRegExp, resourceTypeRegExp, settingsRegExp } from '$lib/utils'
  import LeftArrowIcon from '$lib/LeftArrowIcon.svelte'
  import RightArrowIcon from '$lib/RightArrowIcon.svelte'

  export let turnLangStepOn: boolean
  export let turnBookStepOn: boolean
  export let turnResourceTypeStepOn: boolean
  export let turnSettingsStepOn: boolean
  export let submitLanguages: Function
  export let submitBooks: Function
  export let submitResourceTypes: Function
  export let numLang0ResourceTypes: number
  export let numLang1ResourceTypes: number

  let MAX_LANGUAGES = PUBLIC_MAX_LANGUAGES as unknown as number
</script>

<div
  class="hidden items-center justify-between text-xl font-semibold leading-8 text-[#B3B9C2] sm:flex"
>
  <!-- back button logic -->
  {#if bookRegExp.test($page.url.pathname)}
    <BackButton url="/languages" />
  {:else if resourceTypeRegExp.test($page.url.pathname)}
    <BackButton url="/books" />
  {:else if settingsRegExp.test($page.url.pathname)}
    <BackButton url="/resource_types" />
  {:else}
    <button
      class="flex cursor-not-allowed items-center rounded-md border
             border-[#E5E8EB] bg-white px-4 py-2
             text-xl text-[#33445c]"
      disabled
    >
      <LeftArrowIcon />
      <span class="hidden sm:inline">Back</span>
    </button>
  {/if}
  <!-- breadcrumb link logic -->
  <div class="hidden items-center sm:inline-flex">
    {#if turnLangStepOn}
      <div
        class="flex w-8 items-center justify-center rounded-full text-[#33445C]"
        style="background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%)"
      >
        <span class="text-xl text-white">1</span>
      </div>
    {:else}
      <div class="flex w-8 items-center justify-center rounded-full bg-[#b3b9c2] text-[#33445C]">
        <span class="text-xl text-white">1</span>
      </div>
    {/if}
    {#if turnLangStepOn}
      <span class="ml-2 text-xl text-[#015ad9]"><a href="/languages">Languages</a></span>
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Languages</span>
    {/if}
  </div>
  <div class="hidden items-center sm:inline-flex">
    {#if turnBookStepOn}
      <div
        class="flex w-8 items-center justify-center rounded-full text-[#33445C]"
        style="background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%)"
      >
        <span class="text-xl text-white">2</span>
      </div>
    {:else}
      <div class="flex w-8 items-center justify-center rounded-full bg-[#b3b9c2] text-[#33445C]">
        <span class="text-xl text-white">2</span>
      </div>
    {/if}
    {#if turnBookStepOn}
      <span class="ml-2 text-xl text-[#015ad9]"><a href="/books">Books</a></span>
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Books</span>
    {/if}
  </div>
  <div class="hidden items-center sm:inline-flex">
    {#if turnResourceTypeStepOn}
      <div
        class="flex w-8 items-center justify-center rounded-full text-[#33445C]"
        style="background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%)"
      >
        <span class="text-xl text-white">3</span>
      </div>
    {:else}
      <div class="flex w-8 items-center justify-center rounded-full bg-[#b3b9c2] text-[#33445C]">
        <span class="text-xl text-white">3</span>
      </div>
    {/if}
    {#if turnResourceTypeStepOn}
      <span class="ml-2 text-xl text-[#015ad9]"><a href="/resource_types">Resources</a></span>
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Resources</span>
    {/if}
  </div>
  <div class="hidden items-center sm:inline-flex">
    {#if turnSettingsStepOn}
      <div
        class="flex w-8 items-center justify-center rounded-full text-[#33445C]"
        style="background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%)"
      >
        <span class="text-xl text-white">4</span>
      </div>
    {:else}
      <div class="flex w-8 items-center justify-center rounded-full bg-[#b3b9c2] text-[#33445C]">
        <span class="text-xl text-white">4</span>
      </div>
    {/if}
    {#if turnSettingsStepOn}
      <span class="ml-2 text-xl text-[#015ad9]">Review</span>
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Review</span>
    {/if}
  </div>
  <!-- next button logic -->
  {#if langRegExp.test($page.url.pathname) && $langCountStore > 0 && $langCountStore <= MAX_LANGUAGES}
    <NextButton func={submitLanguages} />
  {:else if bookRegExp.test($page.url.pathname) && $bookCountStore > 0}
    <NextButton func={submitBooks} />
  {:else if resourceTypeRegExp.test($page.url.pathname) && (($langCountStore === 1 && $resourceTypesCountStore > 0) || ($langCountStore === 2 && numLang0ResourceTypes > 0 && numLang1ResourceTypes > 0))}
    <NextButton func={submitResourceTypes} />
  {:else}
    <button
      class="flex cursor-not-allowed items-center rounded-md border
               border-[#E5E8EB] bg-white px-4 py-2
               text-xl text-[#33445c]"
      disabled
    >
      <span class="hidden sm:inline">Next</span>
      <RightArrowIcon />
    </button>
  {/if}
</div>
