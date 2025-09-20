<script lang="ts">
  import { onMount } from 'svelte'
  import {
    PUBLIC_STET_SOURCE_LANG_CODES_NAMES_URL,
    PUBLIC_TAILWIND_SM_MIN_WIDTH,
    PUBLIC_PRODUCTION_DOMAIN
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'
  import Modal from '$lib/Modal.svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import WizardBreadcrumb from '$lib/stet/WizardBreadcrumb.svelte'
  import LanguageSearch from '$lib/LanguageSearch.svelte'
  import WizardBasket from '$lib/stet/WizardBasket.svelte'
  import {
    lang0CodeAndNameStore,
    lang1CodeAndNameStore,
    langCodesStore,
    langCountStore
  } from '$lib/stet/stores/LanguagesStore'
  import { getCode, getName } from '$lib/stet/utils'

  const isProduction = () =>
    window.location.hostname.includes(PUBLIC_PRODUCTION_DOMAIN) ? true : false

  let showGatewayLanguages = true

  // For use by Mobile UI
  let showFilterMenu = false
  let showWizardBasketModal = false

  async function getSourceLangCodesNames(
    apiRootUrl: string = env.PUBLIC_BACKEND_API_URL,
    langCodesAndNamesUrl: string = <string>PUBLIC_STET_SOURCE_LANG_CODES_NAMES_URL
  ): Promise<Array<[string, string, boolean]>> {
    console.log('frontend sees hostname:', window.location.hostname)
    const response = await fetch(`${apiRootUrl}${langCodesAndNamesUrl}`, {
      headers: { 'X-Is-Production': isProduction() ? 'true' : 'false' }
    })
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    return await response.json()
  }

  // Resolve promise for data
  let langCodeNameAndTypes: Array<[string, string, boolean]> = []
  let gatewayCodesAndNames: Array<string> = []
  let heartCodesAndNames: Array<string> = []
  async function loadSourceLangCodesAndNames() {
    try {
      langCodeNameAndTypes = await getSourceLangCodesNames()
      gatewayCodesAndNames = langCodeNameAndTypes
        .filter((element: [string, string, boolean]) => {
          return element[2]
        })
        .map((tuple: [string, string, boolean]) => `${tuple[0]}, ${tuple[1]}`)
      heartCodesAndNames = langCodeNameAndTypes
        .filter((element: [string, string, boolean]) => {
          return !element[2]
        })
        .map((tuple) => `${tuple[0]}, ${tuple[1]}`)
    } catch (err) {
      console.error(err)
    }
  }

  onMount(async () => {
    await loadSourceLangCodesAndNames()
  })

  // Reactive statements for handling languages count
  $: {
    if ($lang0CodeAndNameStore && $lang1CodeAndNameStore) {
      $langCodesStore = [getCode($lang0CodeAndNameStore), getCode($lang1CodeAndNameStore)]
    } else if ($lang0CodeAndNameStore) {
      $langCodesStore = [getCode($lang0CodeAndNameStore)]
    } else if ($lang1CodeAndNameStore) {
      $langCodesStore = [getCode($lang1CodeAndNameStore)]
    } else {
      $langCountStore = 0
      $langCodesStore = []
      $lang0CodeAndNameStore = ''
      $lang1CodeAndNameStore = ''
    }
    $langCountStore = $langCodesStore.length
  }

  // Search field handling for gateway languages
  let gatewaySearchTerm: string = ''
  let filteredGatewayCodeAndNames: Array<string> = []
  $: {
    if (gatewayCodesAndNames) {
      filteredGatewayCodeAndNames = gatewayCodesAndNames.filter(
        (item: string) =>
          getName(item.toLowerCase()).includes(gatewaySearchTerm.toLowerCase()) ||
          getCode(item.toLowerCase()).includes(gatewaySearchTerm.toLowerCase())
      )
    }
  }

  // Search field handling for heart languages
  let heartSearchTerm: string = ''
  let filteredHeartCodeAndNames: Array<string> = []
  $: {
    if (heartCodesAndNames) {
      filteredHeartCodeAndNames = heartCodesAndNames.filter(
        (item: string) =>
          getName(item.toLowerCase()).includes(heartSearchTerm.toLowerCase()) ||
          getCode(item.toLowerCase()).includes(heartSearchTerm.toLowerCase())
      )
    }
  }

  let windowWidth: number = typeof window !== 'undefined' ? window.innerWidth : 0
  $: console.log(`windowWidth: ${windowWidth}`)

  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <!-- center -->
  <div class="flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="ml-4 text-4xl font-normal leading-[48px] text-[#33445C]">
      Select the source language
    </h3>
    <LanguageSearch
      {langCodeNameAndTypes}
      bind:showGatewayLanguages
      bind:gatewaySearchTerm
      bind:showFilterMenu
      bind:showWizardBasketModal
      bind:heartSearchTerm
    />
    {#if (gatewayCodesAndNames && gatewayCodesAndNames.length > 0) || (heartCodesAndNames && heartCodesAndNames.length > 0)}
      {#if windowWidth < TAILWIND_SM_MIN_WIDTH}
        <MobileLanguageDisplay
          {showGatewayLanguages}
          {gatewayCodesAndNames}
          {heartCodesAndNames}
          {filteredHeartCodeAndNames}
          {filteredGatewayCodeAndNames}
        />
      {:else}
        <DesktopLanguageDisplay
          {showGatewayLanguages}
          {gatewayCodesAndNames}
          {heartCodesAndNames}
          {filteredHeartCodeAndNames}
          {filteredGatewayCodeAndNames}
        />
      {/if}
    {/if}
  </div>

  <!-- if isMobile -->
  {#if showWizardBasketModal}
    <WizardBasketModal title="Your selections" bind:showWizardBasketModal>
      <svelte:fragment slot="body">
        <WizardBasket />
      </svelte:fragment>
    </WizardBasketModal>
  {/if}
  <!-- else -->
  <div class="hidden sm:flex sm:w-1/3">
    <WizardBasket />
  </div>
  <!-- end if -->
</div>
