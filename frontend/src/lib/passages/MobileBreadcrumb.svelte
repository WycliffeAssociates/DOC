<script lang="ts">
  import { page } from '$app/stores'
  import BackButton from '$lib/BackButton.svelte'
  import NextButton from '$lib/NextButton.svelte'
  import { langCodesStore } from '$lib/passages/stores/LanguagesStore'
  import { passagesStore } from '$lib/passages/stores/PassagesStore'
  import { getCode, langRegExp, passagesRegExp, settingsRegExp } from '$lib/passages/utils'
  import LeftArrowIcon from '$lib/LeftArrowIcon.svelte'
  import RightArrowIcon from '$lib/RightArrowIcon.svelte'

  export let title: string
  export let stepLabel: string
  export let turnLangStepOn: boolean
  export let turnPassagesStepOn: boolean
  export let turnSettingsStepOn: boolean
  export let submitLanguage: Function
  export let submitPassages: Function
</script>

<div
  class="flex items-center justify-between text-xl text-xl
         font-semibold leading-8 text-[#B3B9C2] sm:hidden"
>
  <!-- mobile only page title -->
  <div>
    <h3 class="text-xl text-[#015AD9]">{title}</h3>
    <h4 class="text-xl text-[#33445C]">Step {stepLabel}</h4>
  </div>
  <div class="flex items-center">
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
      </button>
    {/if}
    <!-- next button logic -->
    {#if langRegExp.test($page.url.pathname) && $langCodesStore}
      <NextButton func={submitLanguage} />
    {:else if passagesRegExp.test($page.url.pathname) && $passagesStore}
      <NextButton func={submitPassages} />
    {:else}
      <button
        class="ml-2 flex cursor-not-allowed items-center rounded-md
                 border border-[#E5E8EB] bg-white px-4 py-2 text-xl text-[#33445c]"
        disabled
      >
        <RightArrowIcon />
      </button>
    {/if}
  </div>
</div>

{#if turnLangStepOn && !turnPassagesStepOn && !turnSettingsStepOn}
  <div class="w-1/4 border border-[#015ad9] sm:hidden" />
{:else if turnPassagesStepOn && !turnSettingsStepOn}
  <div class="w-1/2 border border-[#015ad9] sm:hidden" />
{:else if turnSettingsStepOn}
  <div class="w-full border border-[#015ad9] sm:hidden" />
{/if}
