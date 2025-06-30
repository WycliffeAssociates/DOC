<script lang="ts">
  import { onMount } from 'svelte'
  import { PUBLIC_LANG_CODES_NAMES_URL, PUBLIC_TAILWIND_SM_MIN_WIDTH } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'
  import LanguageSearch from '$lib/LanguageSearch.svelte'
  import WizardBreadcrumb from '$lib/passages/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/passages/WizardBasket.svelte'
  import { langCodeAndNameStore, langCountStore } from '$lib/passages/stores/LanguageStore'
  import { getCode, getName } from '$lib/passages/utils'

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
      $langCodeAndNameStore &&
      heartCodesAndNames.includes($langCodeAndNameStore)
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

  // Resolve promise for data
  let langCodeNameAndTypes: Array<[string, string, boolean]> = []
  let gatewayCodesAndNames: Array<string> = []
  let heartCodesAndNames: Array<string> = []

  async function loadLangCodeNameAndTypes() {
    try {
      langCodeNameAndTypes = await getLangCodesNames()
      gatewayCodesAndNames = langCodeNameAndTypes.filter(([ , , isGateway]) => isGateway)
        .map(([code, name]) => `${code}, ${name}`)
      heartCodesAndNames = langCodeNameAndTypes.filter(([ , , isGateway]) => !isGateway)
        .map(([code, name]) => `${code}, ${name}`)
    } catch (error) {
      console.error(error)
    }
  }

  onMount(async () => {
    await loadLangCodeNameAndTypes()
  })

  // Set $langCountStore
  $: {
    if ($langCodeAndNameStore) {
      console.log(`langCodeAndNameStore: ${langCodeAndNameStore}`)
      $langCountStore = 1
    } else {
      $langCountStore = 0
      $langCodeAndNameStore = ''
    }
  }

  // Search field handling for gateway languages
  let gatewaySearchTerm: string = ''
  let filteredGatewayCodeAndNames: Array<string> = []
  $: {
    if (gatewayCodesAndNames) {
      filteredGatewayCodeAndNames = gatewayCodesAndNames.filter((item: string) =>
        getName(item.toLowerCase()).includes(gatewaySearchTerm.toLowerCase()) || getCode(item.toLowerCase()).includes(gatewaySearchTerm.toLowerCase())
      )
    }
  }

  // Search field handling for heart languages
  let heartSearchTerm: string = ''
  let filteredHeartCodeAndNames: Array<string> = []
  $: {
    if (heartCodesAndNames) {
      filteredHeartCodeAndNames = heartCodesAndNames.filter((item: string) =>
        getName(item.toLowerCase()).includes(heartSearchTerm.toLowerCase()) || getCode(item.toLowerCase()).includes(heartSearchTerm.toLowerCase())
      )
    }
  }

  let windowWidth: number = typeof window !== "undefined" ? window.innerWidth : 0
  $: console.log(`windowWidth: ${windowWidth}`)

  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <!-- center -->
  <div class="flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="ml-4 text-4xl font-normal leading-[48px] text-[#33445C]">Select the language</h3>
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
