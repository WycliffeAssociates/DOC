<script lang="ts">
  import type { PageData } from './$types'
  import {
    PUBLIC_STET_TARGET_LANG_CODES_NAMES_URL,
    PUBLIC_TAILWIND_SM_MIN_WIDTH
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'
  import LanguageSearch from '$lib/LanguageSearch.svelte'
  import WizardBreadcrumb from '$lib/stet/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/stet/WizardBasket.svelte'
  import {
    lang0CodeAndNameStore,
    lang1CodeAndNameStore,
    langCodesStore,
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore,
    langCountStore
  } from '$lib/stet/stores/LanguagesStore'
  import { getCode, getName } from '$lib/stet/utils'

  let showGatewayLanguages = true
  // If user has previously chosen (during this session, i.e., prior
  // to browser reload) any heart languages and no gateway languages then default to
  // showing the heart languages, otherwise the default stands of
  // showing the gateway languages.
  $: {
    if ($lang1CodeAndNameStore && heartCodesAndNames.includes($lang1CodeAndNameStore)) {
      showGatewayLanguages = false
    }
  }
  // For use by Mobile UI
  let showFilterMenu = false
  let showWizardBasketModal = false

  export let data: PageData

  // Track if the user manually changed the tab
  let userInteracted = false

  const selectGatewayTab = () => {
    userInteracted = true
    showGatewayLanguages = true
  }

  const selectHeartTab = () => {
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

  async function getTargetLangCodesNames(
    lang0Code: string,
    apiRootUrl: string = env.PUBLIC_BACKEND_API_URL,
    langCodesAndNamesUrl: string = <string>PUBLIC_STET_TARGET_LANG_CODES_NAMES_URL
  ): Promise<Array<[string, string, boolean]>> {
    const response = await fetch(`${apiRootUrl}${langCodesAndNamesUrl}/${lang0Code}`)
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    return await response.json()
  }

  let langCodeNameAndTypes: Array<[string, string, boolean]> = []
  let gatewayCodesAndNames: Array<string> = []
  let heartCodesAndNames: Array<string> = []
  let lang0Code = data.lang0Code

  async function initializeData() {
    try {
      langCodeNameAndTypes = await getTargetLangCodesNames(lang0Code)
      gatewayCodesAndNames = langCodeNameAndTypes
        .filter((element) => element[2])
        .map((tuple) => `${tuple[0]}, ${tuple[1]}`)
      heartCodesAndNames = langCodeNameAndTypes
        .filter((element) => !element[2])
        .map((tuple) => `${tuple[0]}, ${tuple[1]}`)
    } catch (err) {
      console.error(err) // Consider triggering a toast notification here
    }
  }

  initializeData()

  // Reactive statements for handling languages count
  $: {
    if ($lang0CodeAndNameStore && $lang1CodeAndNameStore) {
      $langCodesStore = [getCode($lang0CodeAndNameStore), getCode($lang1CodeAndNameStore)]
    } else if ($lang0CodeAndNameStore) {
      $langCodesStore = [getCode($lang0CodeAndNameStore)]
    } else if ($lang1CodeAndNameStore) {
      $langCodesStore = [getCode($lang1CodeAndNameStore)]
    } else {
      $langCodesStore = []
    }
    $langCountStore = $langCodesStore.length
  }

  let gatewaySearchTerm: string = ''
  let heartSearchTerm: string = ''
  let filteredGatewayCodeAndNames: Array<string> = []
  let filteredHeartCodeAndNames: Array<string> = []
  // Reactive search filtering
  $: {
    filteredGatewayCodeAndNames = gatewayCodesAndNames.filter((item) =>
      getName(item.toLowerCase()).includes(gatewaySearchTerm.toLowerCase())
    )
    filteredHeartCodeAndNames = heartCodesAndNames.filter((item) =>
      getName(item.toLowerCase()).includes(heartSearchTerm.toLowerCase())
    )
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
      Select the target language
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
    {#if gatewayCodesAndNames && gatewayCodesAndNames.length > 0 && heartCodesAndNames && heartCodesAndNames.length > 0}
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
