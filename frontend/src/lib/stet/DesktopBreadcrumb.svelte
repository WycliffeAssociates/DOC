<script lang="ts">
  import { PUBLIC_MAX_LANGUAGES } from '$env/static/public'
  import { page, navigating } from '$app/stores'
  import BackButton from '$lib/BackButton.svelte'
  import NextButton from '$lib/NextButton.svelte'
  import {
    lang0CodeAndNameStore,
    lang1CodeAndNameStore,
    langCodesStore,
    langCountStore
  } from '$lib/stet/stores/LanguagesStore'
  import { getCode, sourceLangRegExp, targetLangRegExp, settingsRegExp } from '$lib/stet/utils'
  import LeftArrowIcon from '$lib/LeftArrowIcon.svelte'
  import RightArrowIcon from '$lib/RightArrowIcon.svelte'

  export let turnSourceLangStepOn: boolean
  export let turnTargetLangStepOn: boolean
  export let turnSettingsStepOn: boolean
  export let submitSourceLanguage: Function
  export let submitTargetLanguage: Function

  let MAX_LANGUAGES = PUBLIC_MAX_LANGUAGES as unknown as number
</script>

<div
  class="hidden items-center justify-between text-xl font-semibold leading-8 text-[#B3B9C2] sm:flex"
>
  <!-- back button logic -->
  {#if targetLangRegExp.test($page.url.pathname)}
    <BackButton url="/stet/source_languages" />
  {:else if settingsRegExp.test($page.url.pathname)}
    <BackButton url={`/stet/target_languages/${getCode($lang0CodeAndNameStore)}`} />
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
    {#if turnSourceLangStepOn}
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
    {#if turnSourceLangStepOn}
      <span
        class="ml-2 text-xl
                   text-[#015ad9]"><a href="/stet/source_languages">Source Language</a></span
      >
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Source Language</span>
    {/if}
  </div>
  <div class="hidden items-center sm:inline-flex">
    {#if turnTargetLangStepOn}
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
    {#if turnTargetLangStepOn}
      <span
        class="ml-2 text-xl
                   text-[#015ad9]"
        ><a href={`/stet/target_languages/${getCode($lang0CodeAndNameStore)}`}>Target Language</a
        ></span
      >
    {:else}
      <span class="ml-2 text-xl text-[#b3b9c2]">Target Language</span>
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
  {#if sourceLangRegExp.test($page.url.pathname) && $lang0CodeAndNameStore && $langCountStore <= MAX_LANGUAGES}
    <NextButton func={submitSourceLanguage} />
  {:else if targetLangRegExp.test($page.url.pathname) && $lang0CodeAndNameStore && $lang1CodeAndNameStore}
    <NextButton func={submitTargetLanguage} />
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
