<script lang="ts">
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import {
    lang0CodeAndNameStore,
    lang1CodeAndNameStore,
    langCodesStore,
    langCountStore,
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore
  } from '$lib/stet/stores/LanguagesStore'
  import { sourceLangRegExp, getCode, getName } from '$lib/stet/utils'
  import CloseIcon from '$lib/CloseIcon.svelte'
  import EditIcon from '$lib/EditIcon.svelte'
  import GlobeIcon from '$lib/GlobeIcon.svelte'

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

{#if sourceLangRegExp.test($page.url.pathname)}
  <div class="my-2 flex items-center">
    <GlobeIcon />
    <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Source Language</h2>
  </div>
{:else}
  <div class="my-2 flex items-center justify-between">
    <div class="flex items-center justify-between">
      <GlobeIcon />
      <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Source Language</h2>
    </div>
    <button
      class="flex rounded bg-white px-4 py-2 text-xl text-[#33445c] hover:bg-[#efefef]"
      on:click={() => goto('/stet/source_languages')}
    >
      <EditIcon />
      <span class="ml-2"> Edit </span>
    </button>
  </div>
{/if}
{#if $lang0CodeAndNameStore}
  {#if sourceLangRegExp.test($page.url.pathname)}
    <div
      class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
    >
      <div>
        <span>{getName($lang0CodeAndNameStore)}</span><span class="ml-2"
          >({getCode($lang0CodeAndNameStore)})</span
        >
      </div>
      <button
        on:click={() => {
          uncheckGatewayLanguage($lang0CodeAndNameStore)
          uncheckHeartLanguage($lang0CodeAndNameStore)
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
        <span>{getName($lang0CodeAndNameStore)}</span><span class="ml-2"
          >({getCode($lang0CodeAndNameStore)})</span
        >
      </div>
    </div>
  {/if}
{:else}
  <div class="rounded-lg bg-[#e5e8eb] p-6 text-xl text-[#66768b]">
    Selections will appear here once a source language is selected
  </div>
{/if}
