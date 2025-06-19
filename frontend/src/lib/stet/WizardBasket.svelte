<script lang="ts">
  import { goto } from '$app/navigation'
  import { page, navigating } from '$app/stores'
  import {
    lang0CodeAndNameStore,
    lang1CodeAndNameStore,
    langCodesStore,
    langCountStore,
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore
  } from '$lib/stet/stores/LanguagesStore'
  import { sourceLangRegExp, targetLangRegExp, getCode, getName } from '$lib/stet/utils'
  import SourceLanguageBasket from './SourceLanguageBasket.svelte'
  import GlobeIcon from '$lib/GlobeIcon.svelte'
  import EditIcon from '$lib/EditIcon.svelte'
  import CloseIcon from '$lib/CloseIcon.svelte'

  function uncheckGatewayLanguage(langCodeAndName: string) {
    if (langCodeAndName) {
      $gatewayCodeAndNamesStore = $gatewayCodeAndNamesStore.filter(
        (item) => getCode(item) != getCode(langCodeAndName)
      )
      $langCodesStore = $langCodesStore.filter(
        (item) => langCodeAndName && item != getCode(langCodeAndName)
      )
    }
    if (langCodeAndName && $lang0CodeAndNameStore && langCodeAndName === $lang0CodeAndNameStore) {
      $lang0CodeAndNameStore = ''
    }
    if (langCodeAndName && $lang1CodeAndNameStore && langCodeAndName === $lang1CodeAndNameStore) {
      $lang1CodeAndNameStore = ''
    }
    $langCountStore = $langCodesStore.length
  }

  function uncheckHeartLanguage(langCodeAndName: string) {
    if (langCodeAndName) {
      $heartCodeAndNamesStore = $heartCodeAndNamesStore.filter(
        (item) => getCode(item) != getCode(langCodeAndName)
      )
      $langCodesStore = $langCodesStore.filter((item) => item != getCode(langCodeAndName))
    }
    if (langCodeAndName && $lang0CodeAndNameStore && langCodeAndName === $lang0CodeAndNameStore) {
      $lang0CodeAndNameStore = ''
    }
    if (langCodeAndName && $lang1CodeAndNameStore && langCodeAndName === $lang1CodeAndNameStore) {
      $lang1CodeAndNameStore = ''
    }
    $langCountStore = $langCodesStore.length
  }

  $: console.log(
    `$lang0CodeAndNameStore: ${lang0CodeAndNameStore}, $lang1CodeAndNameStore: ${lang1CodeAndNameStore}`
  )
</script>

<div class="w-full flex-shrink-0 overflow-y-auto bg-[#f2f3f5] p-4">
  <h1 class="hidden py-4 pl-0 text-xl font-semibold text-[#33445C] sm:block">Your Selections</h1>
  <SourceLanguageBasket />
  {#if targetLangRegExp.test($page.url.pathname)}
    <div class="my-2 flex items-center">
      <GlobeIcon />
      <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Target Language</h2>
    </div>
  {:else}
    <div class="my-2 flex items-center justify-between">
      <div class="flex items-center justify-between">
        <GlobeIcon />
        <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Target Language</h2>
      </div>
      <button
        class="flex rounded bg-white px-4 py-2 text-xl text-[#33445c] hover:bg-[#efefef]"
        on:click={() =>
          $lang0CodeAndNameStore &&
          goto(`/stet/target_languages/${getCode($lang0CodeAndNameStore)}`)}
        disabled={!$lang0CodeAndNameStore}
      >
        <EditIcon />
        <span class="ml-2"> Edit </span>
      </button>
    </div>
  {/if}
  {#if $lang1CodeAndNameStore && typeof $lang1CodeAndNameStore === 'string'}
    {#if targetLangRegExp.test($page.url.pathname)}
      <div
        class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          <span>{getName($lang1CodeAndNameStore)}</span><span class="ml-2"
            >({getCode($lang1CodeAndNameStore)})</span
          >
        </div>
        <button
          on:click={() => {
            uncheckGatewayLanguage($lang1CodeAndNameStore)
            uncheckHeartLanguage($lang1CodeAndNameStore)
          }}
        >
          <CloseIcon />
        </button>
      </div>
    {:else}
      <div
        class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          <span>{getName($lang1CodeAndNameStore)}</span><span class="ml-2"
            >({getCode($lang1CodeAndNameStore)})</span
          >
        </div>
      </div>
    {/if}
  {:else}
    <div class="rounded-lg bg-[#e5e8eb] p-6 text-xl text-[#66768b]">
      Selections will appear here once a target language is selected
    </div>
  {/if}
</div>
