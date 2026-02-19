<script lang="ts">
  import BibleReferenceSelector from './BibleReferenceSelector.svelte'
  import { handleError } from '$lib/utils'
  import { onMount } from 'svelte'
  import {
    PUBLIC_BOOK_CODES_FROM_USFM_ONLY_URL,
    PUBLIC_TAILWIND_SM_MIN_WIDTH
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import { errorStore } from '$lib/passages/stores/NotificationStore'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import WizardBreadcrumb from '$lib/passages/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/passages/WizardBasket.svelte'
  import { langCodesStore, langCountStore } from '$lib/passages/stores/LanguagesStore'
  import { passagesStore, availablePassagesStore } from '$lib/passages/stores/PassagesStore'
  import CheckIcon from '$lib/CheckIcon.svelte'

  let showWizardBasketModal = false // For use by Mobile UI
  let bookCodesAndNamesLang0: [string, string][] = []
  let bookCodesAndNamesLang1: [string, string][] = []

  async function getBookCodesAndNames(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    bookCodesUrl = <string>PUBLIC_BOOK_CODES_FROM_USFM_ONLY_URL
  ): Promise<[string, string][]> {
    const url = `${apiRootUrl}${bookCodesUrl}${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bookCodesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bookCodesAndNames
  }

  async function loadBookCodesAndNames() {
    try {
      bookCodesAndNamesLang0 = await getBookCodesAndNames($langCodesStore[0])
      if ($langCountStore > 1) {
        bookCodesAndNamesLang1 = await getBookCodesAndNames($langCodesStore[1])
      }
    } catch (err) {
      console.error(err)
      $errorStore = handleError(err)
    } finally {
      console.log('Successfully fetched book codes and names')
    }
  }

  onMount(async () => {
    await loadBookCodesAndNames()
  })

  let windowWidth: number = typeof window !== 'undefined' ? window.innerWidth : 0
  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number

  $: labelString = `Acquiring and analyzing books available for language${$langCountStore > 1 ? 's' : ''} chosen, please be patient`

  $: console.log(`$langCountStore: ${$langCountStore}`)
  $: console.log(`bookCodesAndNamesLang0: ${bookCodesAndNamesLang0}`)
  $: console.log(`bookCodesAndNamesLang1: ${bookCodesAndNamesLang1}`)
  $: console.log(`windowWidth: ${windowWidth}`)
  $: console.log('$passagesStore:', $passagesStore)
  $: console.log('availablePassagesStore:', $availablePassagesStore)
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <main class="flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="mb-4 ml-4 text-4xl font-normal leading-[48px] text-[#33445C]">Add Passages</h3>
    <div class="ml-4 mt-2 flex items-center bg-white px-2 py-2">
      {#if !bookCodesAndNamesLang0 || bookCodesAndNamesLang0.length === 0}
        <div class="ml-4">
          <ProgressIndicator {labelString} />
        </div>
      {:else}
        <BibleReferenceSelector {bookCodesAndNamesLang0} {bookCodesAndNamesLang1} />
        {#if windowWidth < TAILWIND_SM_MIN_WIDTH}
          <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
            <div class="relative">
              <CheckIcon />
              {#if $passagesStore.length > 0}
                <!-- badge -->
                <div
                  class="bg-neutral-focus absolute -right-0.5 -top-0.5
                           h-7 w-7
                           rounded-full
                           text-center text-xl text-[#33445C]"
                  style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                >
                  <span
                    class="text-[8px]
                                   text-white">{$passagesStore.length}</span
                  >
                </div>
              {/if}
            </div>
          </button>
        {/if}
      {/if}
    </div>
  </main>

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
</div>
