<script lang="ts">
  import { onMount } from 'svelte'
  import { PUBLIC_LANGUAGE_BOOK_ORDER } from '$env/static/public'
  import { PUBLIC_LANG_CODES_NAMES_URL, PUBLIC_TAILWIND_SM_MIN_WIDTH } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'
  import WizardBreadcrumb from '$lib/WizardBreadcrumb.svelte'
  import LanguageSearch from '$lib/LanguageSearch.svelte'
  import WizardBasket from '$lib/WizardBasket.svelte'
  import {
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore,
    langCodesStore,
    langCountStore,
    langNamesStore,
    languagesClickedOrderStore
  } from '$lib/stores/LanguagesStore'
  import { ntBookStore, otBookStore, bookCountStore } from '$lib/stores/BooksStore'
  import { getCode, getName, getResourceTypeLangCode } from '$lib/utils'
  import { resourceTypesStore, resourceTypesCountStore } from '$lib/stores/ResourceTypesStore'
  import { assemblyStrategyKindStore } from '$lib/stores/SettingsStore'

  function handleLangChange(e: Event, lang: string) {
    const input = e.currentTarget as HTMLInputElement
    languagesClickedOrderStore.update((arr) => {
      if (input.checked) {
        // append only if not already present
        return arr.includes(lang) ? arr : [...arr, lang]
      } else {
        // remove if unchecked
        return arr.filter((v) => v !== lang)
      }
    })
  }

  let showGatewayLanguages = true
  // Track if the user manually changed the tab:
  let userInteracted = false

  function selectGatewayTab() {
    userInteracted = true
    showGatewayLanguages = true
  }

  function selectHeartTab() {
    userInteracted = true
    showGatewayLanguages = false
  }
  // If user has previously chosen (during this session, i.e., prior
  // to browser reload) any heart languages and no gateway languages then default to
  // showing the heart languages, otherwise the default stands of
  // showing the gateway languages.
  $: {
    if (
      !userInteracted &&
      $heartCodeAndNamesStore.length > 0 &&
      $gatewayCodeAndNamesStore.length === 0
    ) {
      showGatewayLanguages = false
    }
  }
  // For use by Mobile UI
  let showFilterMenu = false
  let showWizardBasketModal = false

  async function getLangCodesNames(
    apiRootUrl: string = env.PUBLIC_BACKEND_API_URL,
    langCodesAndNamesUrl: string = <string>PUBLIC_LANG_CODES_NAMES_URL
  ): Promise<Array<[string, string, boolean]>> {
    const response = await fetch(`${apiRootUrl}${langCodesAndNamesUrl}`)
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    return await response.json()
  }

  let langCodeNameAndTypes: Array<[string, string, boolean]> = []
  let gatewayCodesAndNames: Array<string> = []
  let heartCodesAndNames: Array<string> = []

  async function loadLanguageCodesAndNames() {
    try {
      langCodeNameAndTypes = await getLangCodesNames()
      gatewayCodesAndNames = langCodeNameAndTypes
        .filter(([, , isGateway]) => isGateway)
        .map(([code, name]) => `${code}, ${name}`)
      heartCodesAndNames = langCodeNameAndTypes
        .filter(([, , isGateway]) => !isGateway)
        .map(([code, name]) => `${code}, ${name}`)
    } catch (err) {
      console.error(err)
    }
  }

  onMount(async () => {
    await loadLanguageCodesAndNames()
  })


  $: $langCountStore = $languagesClickedOrderStore ? $languagesClickedOrderStore.length : 0


  $: $langCodesStore = [
    ...($languagesClickedOrderStore ? $languagesClickedOrderStore.map(getCode) : [])
  ]

  $: $langNamesStore = [
    ...($languagesClickedOrderStore ? $languagesClickedOrderStore.map(getName) : [])
  ]

  $: {
    $resourceTypesStore = $resourceTypesStore.filter((item) =>
      $langCodesStore.includes(getResourceTypeLangCode(item))
    )
    $resourceTypesCountStore = $resourceTypesStore.length
  }

  $: {
    if (!$langCountStore) {
      $langCodesStore = []
      $langNamesStore = []
      $resourceTypesStore = []
      $resourceTypesCountStore = 0
      $otBookStore = []
      $ntBookStore = []
      $bookCountStore = 0
      $assemblyStrategyKindStore = <string>PUBLIC_LANGUAGE_BOOK_ORDER
    }
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
      Select up to 2 languages
    </h3>
    <LanguageSearch
      {langCodeNameAndTypes}
      bind:showGatewayLanguages
      bind:userInteracted
      bind:gatewaySearchTerm
      bind:showFilterMenu
      bind:showWizardBasketModal
      bind:heartSearchTerm
      {selectGatewayTab}
      {selectHeartTab}
    />
    {#if gatewayCodesAndNames.length > 0 && heartCodesAndNames.length > 0}
      {#if windowWidth < TAILWIND_SM_MIN_WIDTH}
        <MobileLanguageDisplay
          {handleLangChange}
          {showGatewayLanguages}
          {gatewayCodesAndNames}
          {heartCodesAndNames}
          {filteredHeartCodeAndNames}
          {filteredGatewayCodeAndNames}
        />
      {:else}
        <DesktopLanguageDisplay
          {handleLangChange}
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
