<script lang="ts">
  import type { PassageReferenceDto } from '$lib/passages/models'
  import BibleReferenceSelector from './BibleReferenceSelector.svelte'
  import { onMount } from 'svelte'
  import {
    PUBLIC_BOOK_CODES_FROM_USFM_ONLY_URL,
    PUBLIC_TAILWIND_SM_MIN_WIDTH
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import WizardBreadcrumb from '$lib/passages/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/passages/WizardBasket.svelte'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguageStore'
  import { passagesStore, addPassageReference } from '$lib/passages/stores/PassagesStore'
  import CheckIcon from '$lib/CheckIcon.svelte'

  // For use by Mobile UI
  let showWizardBasketModal = false

  async function getBookCodesAndNames(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    bookCodesUrl = <string>PUBLIC_BOOK_CODES_FROM_USFM_ONLY_URL
  ): Promise<Array<[string, string]>> {
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

  let bookCodesAndNames: Array<[string, string]> = []

  onMount(() => {
    let langCode = $langCodeAndNameStore.split(',')[0]
    console.log(langCode)
    console.log(`langCode: ${JSON.stringify(langCode)}`)
    getBookCodesAndNames(langCode)
      .then((bookCodesAndNames_) => {
        bookCodesAndNames = [...bookCodesAndNames_] // Ensure reactivity with [...blah]
      })
      .catch((err) => console.error(err))
  })

  function removePassage(id: number) {
    $passagesStore = $passagesStore.filter((item: PassageReferenceDto) => item.id != id)
  }

  $: if (bookCodesAndNames && bookCodesAndNames.length > 0) {
    for (let passageReferenceDto of $passagesStore) {
      if (!bookCodesAndNames.map(([bookCode]) => bookCode).includes(passageReferenceDto.bookCode)) {
        removePassage(passageReferenceDto.id)
      }
    }
  }

  let windowWidth: number = typeof window !== 'undefined' ? window.innerWidth : 0
  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number

  $: console.log(`windowWidth: ${windowWidth}`)
  $: console.log(`$passagesStore: ${JSON.stringify($passagesStore)}`)
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <div class="flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="ml-4 text-4xl font-normal leading-[48px] text-[#33445C]">Add Passages</h3>
    <div class="ml-4 mt-2 flex items-center bg-white px-2 py-2">
      {#if !bookCodesAndNames || bookCodesAndNames.length === 0}
        <div class="ml-4">
          <ProgressIndicator
            labelString="Acquiring and analyzing books available for language chosen, please be patient"
          />
        </div>
      {:else}
        <BibleReferenceSelector {bookCodesAndNames} />
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
</div>
