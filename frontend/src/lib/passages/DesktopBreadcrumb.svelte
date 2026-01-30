<script lang="ts">
  import { PUBLIC_MAX_LANGUAGES } from '$env/static/public'
  import { page, navigating } from '$app/stores'
  import BackButton from '$lib/BackButton.svelte'
  import NextButton from '$lib/NextButton.svelte'
  import { langCodesStore } from '$lib/passages/stores/LanguagesStore'
  import { passagesStore } from '$lib/passages/stores/PassagesStore'
  import { getCode, langRegExp, passagesRegExp, settingsRegExp } from '$lib/passages/utils'
  import LeftArrowIcon from '$lib/LeftArrowIcon.svelte'
  import RightArrowIcon from '$lib/RightArrowIcon.svelte'

  export let turnLangStepOn: boolean
  export let turnPassagesStepOn: boolean
  export let turnSettingsStepOn: boolean
  export let submitLanguage: Function
  export let submitPassages: Function
</script>

<div
  class="hidden items-center justify-between text-xl font-semibold leading-8 text-[#B3B9C2] sm:flex"
>
  <!-- back button logic -->
  {#if passagesRegExp.test($page.url.pathname)}
    <BackButton url="/passages/language" />
  {:else if settingsRegExp.test($page.url.pathname)}
    <BackButton url={`/passages/passages`} />
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
      <span
        class="ml-2 text-xl
                   text-[#015ad9]"><a href="/passages/language">Language</a></span
      >
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Language</span>
    {/if}
  </div>
  <div class="hidden items-center sm:inline-flex">
    {#if turnPassagesStepOn}
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
    {#if turnPassagesStepOn}
      <span
        class="ml-2 text-xl
                   text-[#015ad9]"><a href={`/passages/passages`}>Passages</a></span
      >
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Passages</span>
    {/if}
  </div>
  <div class="hidden items-center sm:inline-flex">
    {#if turnSettingsStepOn}
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
    {#if turnSettingsStepOn}
      <span class="ml-2 text-xl text-[#015ad9]">Review</span>
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Review</span>
    {/if}
  </div>
  <!-- next button logic -->
  {#if langRegExp.test($page.url.pathname) && $langCodesStore}
    <NextButton func={submitLanguage} />
  {:else if passagesRegExp.test($page.url.pathname) && $passagesStore}
    <NextButton func={submitPassages} />
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
