<script lang="ts">
  import { onMount } from 'svelte'
  import {
    PUBLIC_SHARED_RESOURCE_TYPES_URL,
    PUBLIC_TAILWIND_SM_MIN_WIDTH
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBreadcrumb from '$lib/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/WizardBasket.svelte'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import { ntBookStore, otBookStore } from '$lib/stores/BooksStore'
  import { langCodesStore, langNamesStore, langCountStore } from '$lib/stores/LanguagesStore'
  import { bookCountStore } from '$lib/stores/BooksStore'
  import {
    limitTwStore,
    resourceTypesStore,
    resourceTypesCountStore,
    twResourceRequestedStore,
    usfmAvailableStore
  } from '$lib/stores/ResourceTypesStore'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import {
    getCode,
    getName,
    getResourceTypeLangCode,
    getResourceTypeCode,
    getResourceTypeName
  } from '$lib/utils'
  import CheckIcon from '$lib/CheckIcon.svelte'

  async function getResourceTypesAndNames(
    langCode: string,
    bookCodeAndNames: Array<[string, string]>,
    apiRootUrl = <string>env.PUBLIC_BACKEND_API_URL,
    sharedResourceTypesUrl = <string>PUBLIC_SHARED_RESOURCE_TYPES_URL
  ): Promise<Array<[string, string, string]>> {
    let book_codes = bookCodeAndNames.map(([code]) => code).join(',')
    const url = new URL(`${apiRootUrl}${sharedResourceTypesUrl}${langCode}/${book_codes}`)
    console.log(`About to send request ${url} to backend`)
    const response = await fetch(url)
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    const resourceTypesAndNames: Array<[string, string]> = await response.json()
    return resourceTypesAndNames.map(([code, name]) => [langCode, code, name])
  }

  let otBookCodes: Array<[string, string]> = $otBookStore.map((item) => [
    getCode(item),
    getName(item)
  ])

  let ntBookCodes: Array<[string, string]> = $ntBookStore.map((item) => [
    getCode(item),
    getName(item)
  ])

  let lang0ResourceTypesAndNames: Array<string>
  let lang1ResourceTypesAndNames: Array<string>
  onMount(async () => {
    if ($langCodesStore[0]) {
      try {
        const resourceTypesAndNames = await getResourceTypesAndNames($langCodesStore[0], [
          ...otBookCodes,
          ...ntBookCodes
        ])
        lang0ResourceTypesAndNames = resourceTypesAndNames.map(([lang, code, name]) =>
          [lang, code, name].join(', ')
        )
      } catch (err) {
        console.error(err)
      }
    }
    if ($langCodesStore[1]) {
      try {
        const resourceTypesAndNames_ = await getResourceTypesAndNames($langCodesStore[1], [
          ...otBookCodes,
          ...ntBookCodes
        ])
        lang1ResourceTypesAndNames = resourceTypesAndNames_.map(([lang, code, name]) =>
          [lang, code, name].join(', ')
        )
      } catch (err) {
        console.error(err)
      }
    }
  })

  $: $resourceTypesCountStore = $resourceTypesStore.every((item) => item.length > 0)
    ? $resourceTypesStore.length
    : 0

  let showWizardBasketModal = false

  // Set whether a USFM type is available for any of the languages
  // requested so that we can use this fact in the UI to trigger the
  // presence or absence of the toggle to limit TW words.
  let usfmRegexp = /\S*(avd|ayt|blv|cuv|f10|nav|reg|ugnt|uhb|ulb|usfm)\S*/
  $: {
    $usfmAvailableStore = $resourceTypesStore.some((item) => usfmRegexp.test(item)) || false
  }

  // Set whether TW has been requested for any of the languages
  // requested so that we can use this fact in the UI to trigger the
  // presence or absence of the toggle to limit TW words.
  let twRegexp = new RegExp('.*tw.*')
  $: {
    $twResourceRequestedStore =
      $resourceTypesStore && $resourceTypesStore.some((item) => twRegexp.test(item))
  }
  $: {
    $limitTwStore = $twResourceRequestedStore && $usfmAvailableStore
  }

  // --- MUTUAL EXCLUSIVITY LOGIC ---
  // Track the previous state of the store to determine which note option was checked last
  let previousResourceTypes: Array<string> = []

  $: {
    // Only run mutual exclusivity checks if the store actually changed
    if (JSON.stringify($resourceTypesStore) !== JSON.stringify(previousResourceTypes)) {
      let updatedStore = [...$resourceTypesStore]
      let storeChanged = false

      // Group resources by language code to handle cross-contamination safely
      const languagesInStore = [
        ...new Set(updatedStore.map((item) => getResourceTypeLangCode(item)))
      ]

      for (const lang of languagesInStore) {
        // Find items in the current selection for this language
        const langItems = updatedStore.filter((item) => getResourceTypeLangCode(item) === lang)
        const hasTN = langItems.some((item) => getResourceTypeName(item) === 'Translation Notes')
        const hasCTN = langItems.some(
          (item) => getResourceTypeName(item) === 'Condensed Translation Notes'
        )

        // If both are present, determine which one was added last
        if (hasTN && hasCTN) {
          const prevLangItems = previousResourceTypes.filter(
            (item) => getResourceTypeLangCode(item) === lang
          )
          const prevHadTN = prevLangItems.some(
            (item) => getResourceTypeName(item) === 'Translation Notes'
          )
          const prevHadCTN = prevLangItems.some(
            (item) => getResourceTypeName(item) === 'Condensed Translation Notes'
          )

          if (prevHadTN && !prevHadCTN) {
            // "Condensed" was just checked, remove standard "Translation Notes"
            updatedStore = updatedStore.filter(
              (item) =>
                !(
                  getResourceTypeLangCode(item) === lang &&
                  getResourceTypeName(item) === 'Translation Notes'
                )
            )
            storeChanged = true
          } else {
            // "Translation Notes" was just checked (or it's an ambiguous state), remove "Condensed"
            updatedStore = updatedStore.filter(
              (item) =>
                !(
                  getResourceTypeLangCode(item) === lang &&
                  getResourceTypeName(item) === 'Condensed Translation Notes'
                )
            )
            storeChanged = true
          }
        }
      }

      if (storeChanged) {
        $resourceTypesStore = updatedStore
      }
      previousResourceTypes = [...$resourceTypesStore]
    }
  }
  // ---------------------------------

  $: console.log(`lang0ResourceTypesAndNames: ${lang0ResourceTypesAndNames}`)
  $: console.log(`lang1ResourceTypesAndNames: ${lang1ResourceTypesAndNames}`)
  $: console.log(`$twResourceRequestedStore: ${$twResourceRequestedStore}`)
  $: console.log(`$limitTwStore: ${$limitTwStore}`)
  $: console.log(`$resourceTypesStore: ${$resourceTypesStore}`)
  $: console.log(`$usfmAvailableStore: ${$usfmAvailableStore}`)

  function selectAllLang0ResourceTypes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      // Filter out 'Condensed Translation Notes' when Select All is clicked
      lang0ResourceTypesAndNames
        .filter((item) => getResourceTypeCode(item) !== 'tn-condensed')
        .map((item) => $resourceTypesStore.push(item))

      $resourceTypesStore = [...new Set($resourceTypesStore)]
      $resourceTypesCountStore = $resourceTypesStore.length
    } else {
      $resourceTypesStore = $resourceTypesStore.filter(
        (item) => $langCodesStore[0] !== getResourceTypeLangCode(item)
      )
    }
  }

  function selectAllLang1ResourceTypes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      // Filter out 'Condensed Translation Notes' when Select All is clicked
      lang1ResourceTypesAndNames
        .filter((item) => getResourceTypeCode(item) !== 'tn-condensed')
        .map((item) => $resourceTypesStore.push(item))

      $resourceTypesStore = [...new Set($resourceTypesStore)]
      $resourceTypesCountStore = $resourceTypesStore.length
    } else {
      $resourceTypesStore = $resourceTypesStore.filter(
        (item) => $langCodesStore[1] !== getResourceTypeLangCode(item)
      )
    }
  }

  let windowWidth: number = typeof window !== 'undefined' ? window.innerWidth : 0
  $: console.log(`windowWidth: ${windowWidth}`)

  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <div class="mx-4 mb-6 flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="mb-4 text-4xl font-normal leading-[48px] text-[#33445C]">Pick your resources</h3>
    <!-- mobile basket modal launcher -->
    <div class="mr-4 text-right sm:hidden">
      <button on:click={() => (showWizardBasketModal = true)}>
        <div class="relative">
          <CheckIcon />
          {#if $langCountStore > 0 || $bookCountStore > 0 || $resourceTypesCountStore > 0}
            <!-- badge -->
            <div
              class="bg-neutral-focus absolute -right-0.5 -top-0.5
                        h-7 w-7
                        rounded-full text-center text-xl text-[#33445C]"
              style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
            >
              <span
                class="text-[8px]
                          text-white"
                >{$langCountStore + $bookCountStore + $resourceTypesCountStore}</span
              >
            </div>
          {/if}
        </div>
      </button>
    </div>
    {#if ($langCountStore > 0 && (!lang0ResourceTypesAndNames || (lang0ResourceTypesAndNames && lang0ResourceTypesAndNames.length == 0))) || ($langCountStore > 1 && (!lang1ResourceTypesAndNames || (lang1ResourceTypesAndNames && lang1ResourceTypesAndNames.length == 0)))}
      <ProgressIndicator
        labelString="Acquiring and analyzing resources available for languages and books chosen, please be patient"
      />
    {:else if windowWidth < TAILWIND_SM_MIN_WIDTH}
      {#if $langCountStore > 0}
        <div>
          <h3 class="text-2xl text-[#33445C]">{$langNamesStore[0]}</h3>
        </div>
      {/if}
      <div>
        {#if lang0ResourceTypesAndNames && lang0ResourceTypesAndNames.length > 0}
          <div>
            <div class="flex items-center py-2 pl-4">
              <input
                id="select-all-lang0-resource-types"
                type="checkbox"
                class="checkbox-target checkbox-style"
                on:change={(event) => selectAllLang0ResourceTypes(event)}
              />
              <label for="select-all-lang0-resource-types" class="pl-1 text-xl text-[#33445C]"
                >Select all</label
              >
            </div>
            {#each lang0ResourceTypesAndNames as lang0ResourceTypeAndName, index}
              <label for="lang0-resourcetype-{index}">
                <div class="target flex h-[56px] items-center justify-between px-4">
                  <div class="target2 flex items-center">
                    <input
                      id="lang0-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$resourceTypesStore}
                      value={lang0ResourceTypeAndName}
                      class="checkbox-target checkbox-style"
                    />
                    <span class="pl-1 text-xl text-[#33445C]"
                      >{getResourceTypeName(lang0ResourceTypeAndName)}</span
                    >
                  </div>
                  <span class="text-xl text-[#33445C]"
                    >{getResourceTypeCode(lang0ResourceTypeAndName)}</span
                  >
                </div>
              </label>
            {/each}
          </div>
        {/if}
        {#if $langCountStore > 1}
          <div>
            <h3 class="text-2xl text-[#33445C]">{$langNamesStore[1]}</h3>
          </div>
        {/if}
        {#if lang1ResourceTypesAndNames && lang1ResourceTypesAndNames.length > 0}
          <div>
            <div class="flex items-center py-2 pl-4">
              <input
                id="select-all-lang1-resource-types"
                type="checkbox"
                class="checkbox-target checkbox-style"
                on:change={(event) => selectAllLang1ResourceTypes(event)}
              />
              <label for="select-all-lang1-resource-types" class="pl-1 text-xl text-[#33445C]"
                >Select all</label
              >
            </div>
            {#each lang1ResourceTypesAndNames as lang1ResourceTypeAndName, index}
              <label for="lang1-resourcetype-{index}">
                <div class="target flex h-[56px] items-center justify-between px-4">
                  <div class="target2 flex items-center">
                    <input
                      id="lang1-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$resourceTypesStore}
                      value={lang1ResourceTypeAndName}
                      class="checkbox-target checkbox-style"
                    />
                    <span class="pl-1 text-xl text-[#33445C]"
                      >{getResourceTypeName(lang1ResourceTypeAndName)}</span
                    >
                  </div>
                  <span class="text-xl text-[#33445C]"
                    >{getResourceTypeCode(lang1ResourceTypeAndName)}</span
                  >
                </div>
              </label>
            {/each}
          </div>
        {/if}
      </div>
    {:else}
      <div class="mb-2 flex flex-shrink-0 flex-grow-0 flex-row">
        {#if $langCountStore > 0}
          <div class={$langCountStore > 1 ? 'w-1/2' : 'w-full'}>
            <h3 class="text-2xl text-[#33445C]">{$langNamesStore[0]}</h3>
          </div>
        {/if}
        {#if $langCountStore > 1 && lang1ResourceTypesAndNames}
          <div class={$langCountStore > 1 ? 'w-1/2' : 'w-full'}>
            <h3 class="text-2xl text-[#33445C]">{$langNamesStore[1]}</h3>
          </div>
        {/if}
      </div>
      <div class="flex flex-shrink-0 flex-grow-0 flex-row">
        {#if lang0ResourceTypesAndNames && lang0ResourceTypesAndNames.length > 0}
          <div class={$langCountStore > 1 ? 'w-1/2' : 'w-full'}>
            <div class="flex items-center py-2 pl-4">
              <input
                id="select-all-lang0-resource-types"
                type="checkbox"
                class="checkbox-target checkbox-style"
                on:change={(event) => selectAllLang0ResourceTypes(event)}
              />
              <label for="select-all-lang0-resource-types" class="pl-1 text-xl text-[#33445C]"
                >Select all</label
              >
            </div>
            {#each lang0ResourceTypesAndNames as lang0ResourceTypeAndName, index}
              <label for="lang0-resourcetype-{index}">
                <div class="target flex h-[56px] items-center justify-between px-4">
                  <div class="target2 flex items-center">
                    <input
                      id="lang0-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$resourceTypesStore}
                      value={lang0ResourceTypeAndName}
                      class="checkbox-target checkbox-style"
                    />
                    <span class="pl-1 text-xl text-[#33445C]"
                      >{getResourceTypeName(lang0ResourceTypeAndName)}</span
                    >
                  </div>
                  <span class="text-xl text-[#33445C]"
                    >{getResourceTypeCode(lang0ResourceTypeAndName)}</span
                  >
                </div>
              </label>
            {/each}
          </div>
        {/if}
        {#if lang1ResourceTypesAndNames && lang1ResourceTypesAndNames.length > 0}
          <div class={$langCountStore > 1 ? 'ml-4 w-1/2' : 'ml-4 w-full'}>
            <div class="flex items-center py-2 pl-4">
              <input
                id="select-all-lang1-resource-types"
                type="checkbox"
                class="checkbox-target checkbox-style"
                on:change={(event) => selectAllLang1ResourceTypes(event)}
              />
              <label for="select-all-lang1-resource-types" class="pl-1 text-xl text-[#33445C]"
                >Select all</label
              >
            </div>
            {#each lang1ResourceTypesAndNames as lang1ResourceTypeAndName, index}
              <label for="lang1-resourcetype-{index}">
                <div class="target flex h-[56px] items-center justify-between px-4">
                  <div class="target2 flex items-center">
                    <input
                      id="lang1-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$resourceTypesStore}
                      value={lang1ResourceTypeAndName}
                      class="checkbox-target checkbox-style"
                    />
                    <span class="pl-1 text-xl text-[#33445C]"
                      >{getResourceTypeName(lang1ResourceTypeAndName)}</span
                    >
                  </div>
                  <span class="text-xl text-[#33445C]"
                    >{getResourceTypeCode(lang1ResourceTypeAndName)}</span
                  >
                </div>
              </label>
            {/each}
          </div>
        {/if}
      </div>
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
