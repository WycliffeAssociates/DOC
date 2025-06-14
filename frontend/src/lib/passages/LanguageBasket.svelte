<script lang="ts">
  import { goto } from '$app/navigation'
  import { page } from '$app/stores'
  import {
    langCodeAndNameStore,
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore
  } from '$lib/passages/stores/LanguageStore'
  import { langRegExp, getCode, getName } from '$lib/passages/utils'
  import CloseIcon from '$lib/CloseIcon.svelte'
  import EditIcon from '$lib/EditIcon.svelte'
  import GlobeIcon from '$lib/GlobeIcon.svelte'

  function uncheckGatewayLanguage(langCodeAndName: string) {
    if (langCodeAndName) {
      $gatewayCodeAndNamesStore = $gatewayCodeAndNamesStore.filter(
        (item) => getCode(item) != getCode(langCodeAndName)
      )
    }
    if (langCodeAndName && $langCodeAndNameStore && langCodeAndName === $langCodeAndNameStore) {
      $langCodeAndNameStore = ''
    }
  }

  function uncheckHeartLanguage(langCodeAndName: string) {
    if (langCodeAndName) {
      $heartCodeAndNamesStore = $heartCodeAndNamesStore.filter(
        (item) => getCode(item) != getCode(langCodeAndName)
      )
    }
    if (langCodeAndName && $langCodeAndNameStore && langCodeAndName === $langCodeAndNameStore) {
      $langCodeAndNameStore = ''
    }
  }

  $: console.log(`$langCodeAndNameStore: ${JSON.stringify(langCodeAndNameStore, null, 2)}`)
</script>

{#if langRegExp.test($page.url.pathname)}
  <div class="my-2 flex items-center">
    <GlobeIcon />
    <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Language</h2>
  </div>
{:else}
  <div class="my-2 flex items-center justify-between">
    <div class="flex items-center justify-between">
      <GlobeIcon />
      <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Language</h2>
    </div>
    <button
      class="flex rounded bg-white px-4 py-2 text-xl text-[#33445c] hover:bg-[#efefef]"
      on:click={() => goto('/passages/language')}
    >
      <EditIcon />
      <span class="ml-2"> Edit </span>
    </button>
  </div>
{/if}
{#if $langCodeAndNameStore}
  {#if langRegExp.test($page.url.pathname)}
    <div
      class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
    >
      <div>
        <span>{getName($langCodeAndNameStore)}</span><span class="ml-2"
          >({getCode($langCodeAndNameStore)})</span
        >
      </div>
      <button
        on:click={() => {
          uncheckGatewayLanguage($langCodeAndNameStore)
          uncheckHeartLanguage($langCodeAndNameStore)
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
        <span>{getName($langCodeAndNameStore)}</span><span class="ml-2"
          >({getCode($langCodeAndNameStore)})</span
        >
      </div>
    </div>
  {/if}
{:else}
  <div class="rounded-lg bg-[#e5e8eb] p-6 text-xl text-[#66768b]">
    Language will appear here selected
  </div>
{/if}
