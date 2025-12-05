<script lang="ts">
  import type { Writable } from 'svelte/store'
  import { onMount } from 'svelte'
  import type { ComponentType } from 'svelte'
  import { PUBLIC_TAILWIND_SM_MIN_WIDTH } from '$env/static/public'
  import { getCode, getName, loadLangCodesNames } from '$lib/utils'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import LanguageSearch from '$lib/LanguageSearch.svelte'

  export let WizardBreadcrumb: ComponentType
  export let WizardBasket: ComponentType

  export let MobileLanguageDisplay: ComponentType
  export let DesktopLanguageDisplay: ComponentType
  export let languagesClickedOrderStore: Writable<Array<string>>
  export let langCodesStore: Writable<Array<string>>
  export let langNamesStore: Writable<Array<string>>
  export let langCountStore: Writable<number>

  export let message: string

  let showGatewayLanguages = true

  // For use by Mobile UI
  let showFilterMenu = false
  let showWizardBasketModal = false

  let langCodeNameAndTypes: Array<[string, string, boolean]> = []
  let gatewayCodesAndNames: Array<string> = []
  let heartCodesAndNames: Array<string> = []

  onMount(async () => {
    try {
      ;[langCodeNameAndTypes, gatewayCodesAndNames, heartCodesAndNames] = await loadLangCodesNames()
    } catch (err) {
      console.error(err)
    }
  })

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

  $: $langCountStore = $languagesClickedOrderStore ? $languagesClickedOrderStore.length : 0

  $: $langCodesStore = [
    ...($languagesClickedOrderStore ? $languagesClickedOrderStore.map(getCode) : [])
  ]

  $: $langNamesStore = [
    ...($languagesClickedOrderStore ? $languagesClickedOrderStore.map(getName) : [])
  ]

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

<svelte:component this={WizardBreadcrumb} />

<!-- container for "center" div -->
<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <!-- center -->
  <div class="flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="ml-4 text-4xl font-normal leading-[48px] text-[#33445C]">
      {message}
    </h3>
    <LanguageSearch
      {langCodeNameAndTypes}
      bind:showGatewayLanguages
      bind:gatewaySearchTerm
      bind:showFilterMenu
      bind:showWizardBasketModal
      bind:heartSearchTerm
    />
    {#if gatewayCodesAndNames && gatewayCodesAndNames.length > 0 && heartCodesAndNames && heartCodesAndNames.length > 0}
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
          {filteredGatewayCodeAndNames}
          {filteredHeartCodeAndNames}
        />
      {/if}
    {/if}
  </div>

  <!-- if isMobile -->
  {#if showWizardBasketModal}
    <WizardBasketModal title="Your selections" bind:showWizardBasketModal>
      <svelte:fragment slot="body">
        <svelte:component this={WizardBasket} />
      </svelte:fragment>
    </WizardBasketModal>
  {/if}
  <!-- else -->
  <div class="hidden sm:flex sm:w-1/3">
    <svelte:component this={WizardBasket} />
  </div>
  <!-- end if -->
</div>
