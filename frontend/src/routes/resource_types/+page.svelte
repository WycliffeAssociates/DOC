<script lang="ts">
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
    resourceTypesStore,
    resourceTypesCountStore,
    usfmAvailableStore
  } from '$lib/stores/ResourceTypesStore'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import { getCode, getName, getResourceTypeLangCode, getResourceTypeName } from '$lib/utils'

  async function getResourceTypesAndNames(
    langCode: string,
    bookCodeAndNames: Array<[string, string]>,
    apiRootUrl = <string>env.PUBLIC_BACKEND_API_URL,
    sharedResourceTypesUrl = <string>PUBLIC_SHARED_RESOURCE_TYPES_URL
  ): Promise<Array<[string, string, string]>> {
    // Form the URL to ultimately invoke
    // resource_lookup.resource_types.
    let book_codes = bookCodeAndNames.map((bookCodeAndName) => bookCodeAndName[0]).join(',')
    const url_ = `${apiRootUrl}${sharedResourceTypesUrl}${langCode}/${book_codes}`
    const url = new URL(url_)
    console.log(`About to send request ${url} to backend`)
    const response = await fetch(url)
    const resourceTypesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    // Associate the langCode to each resource type code and name pair
    return resourceTypesAndNames.map((element) => [langCode, element[0], element[1]])
  }

  // Resolve promise for data
  let lang0ResourceTypesAndNames: Array<string>
  let otBookCodes_: Array<[string, string]> = $otBookStore.map((item) => [
    getCode(item),
    getName(item)
  ])
  let ntBookCodes_: Array<[string, string]> = $ntBookStore.map((item) => [
    getCode(item),
    getName(item)
  ])
  // Resolve promise for data
  if ($langCodesStore[0]) {
    getResourceTypesAndNames($langCodesStore[0], [...otBookCodes_, ...ntBookCodes_])
      .then((resourceTypesAndNames) => {
        lang0ResourceTypesAndNames = resourceTypesAndNames.map(
          (tuple) => `${tuple[0]}, ${tuple[1]}, ${tuple[2]}`
        )
      })
      .catch((err) => console.error(err))
  }

  // Resolve promise for data for language
  let lang1ResourceTypesAndNames: Array<string>
  if ($langCodesStore[1]) {
    getResourceTypesAndNames($langCodesStore[1], [...otBookCodes_, ...ntBookCodes_])
      .then((resourceTypesAndNames) => {
        lang1ResourceTypesAndNames = resourceTypesAndNames.map(
          (tuple) => `${tuple[0]}, ${tuple[1]}, ${tuple[2]}`
        )
      })
      .catch((err) => console.error(err))
  }

  let nonEmptyResourcetypes: boolean
  $: nonEmptyResourcetypes = $resourceTypesStore.every((item) => item.length > 0)

  $: {
    if (nonEmptyResourcetypes) {
      $resourceTypesCountStore = $resourceTypesStore.length
    } else {
      $resourceTypesCountStore = 0
    }
  }

  let showWizardBasketModal = false

  function selectAllLang0ResourceTypes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      // Make sure all the lang0 resource types are added to
      // resourceTypesStore.
      lang0ResourceTypesAndNames.map((item) => $resourceTypesStore.push(item))
      // Get rid of duplicates
      $resourceTypesStore = [...new Set($resourceTypesStore)]
      // Set the resourceTypesCountStore
      $resourceTypesCountStore = $resourceTypesStore.length
    } else {
      // Remove any lang0 resource types from the resourceTypesStore
      $resourceTypesStore = $resourceTypesStore.filter(
        (item) => $langCodesStore[0] !== getResourceTypeLangCode(item)
      )
    }
  }
  function selectAllLang1ResourceTypes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      // Make sure all the lang0 resource types are added to
      // resourceTypesStore.
      lang1ResourceTypesAndNames.map((item) => $resourceTypesStore.push(item))
      // Get rid of duplicates
      $resourceTypesStore = [...new Set($resourceTypesStore)]
      // Set the resourceTypesCountStore
      $resourceTypesCountStore = $resourceTypesStore.length
    } else {
      // Remove any lang1 resource types from the resourceTypesStore
      $resourceTypesStore = $resourceTypesStore.filter(
        (item) => $langCodesStore[1] !== getResourceTypeLangCode(item)
      )
    }
  }

  // Set whether a USFM type is available for any of the languages
  // requested so that we can use this fact in the UI to trigger the
  // presence or absence of the toggle to limit TW words.
  let usfmRegexp = /\S*(avd|ayt|blv|cuv|f10|nav|reg|ugnt|uhb|ulb|usfm)\S*/
  $: {
    if (
      lang0ResourceTypesAndNames &&
      lang0ResourceTypesAndNames.length > 0 &&
      lang1ResourceTypesAndNames &&
      lang1ResourceTypesAndNames.length > 0
    ) {
      $usfmAvailableStore =
        lang0ResourceTypesAndNames.some((item) => usfmRegexp.test(item)) ||
        lang1ResourceTypesAndNames.some((item) => usfmRegexp.test(item))
    } else if (
      lang0ResourceTypesAndNames &&
      lang0ResourceTypesAndNames.length > 0 &&
      !lang1ResourceTypesAndNames
    ) {
      $usfmAvailableStore = lang0ResourceTypesAndNames.some((item) => usfmRegexp.test(item))
    }
  }

  let windowWidth: number
  $: console.log(`windowWidth: ${windowWidth}`)

  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number
  // $: console.log(`TAILWIND_SM_MIN_WIDTH: ${TAILWIND_SM_MIN_WIDTH}`)
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <!-- center -->
  <div class="mx-4 mb-6 flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="mb-4 text-4xl font-normal leading-[48px] text-[#33445C]">Pick your resources</h3>
    <!-- mobile basket modal launcher -->
    <div class="mr-4 text-right sm:hidden">
      <button on:click={() => (showWizardBasketModal = true)}>
        <div class="relative">
          <svg
            width="56"
            height="48"
            viewBox="0 0 56 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M35 15H21C19.9 15 19 15.9 19 17V31C19 32.1 19.9 33 21 33H35C36.1 33 37 32.1 37 31V17C37 15.9 36.1 15 35 15ZM26.71 28.29C26.6175 28.3827 26.5076 28.4563 26.3866 28.5064C26.2657 28.5566 26.136 28.5824 26.005 28.5824C25.874 28.5824 25.7443 28.5566 25.6234 28.5064C25.5024 28.4563 25.3925 28.3827 25.3 28.29L21.71 24.7C21.6174 24.6074 21.544 24.4975 21.4939 24.3765C21.4438 24.2556 21.418 24.1259 21.418 23.995C21.418 23.8641 21.4438 23.7344 21.4939 23.6135C21.544 23.4925 21.6174 23.3826 21.71 23.29C21.8026 23.1974 21.9125 23.124 22.0335 23.0739C22.1544 23.0238 22.2841 22.998 22.415 22.998C22.5459 22.998 22.6756 23.0238 22.7965 23.0739C22.9175 23.124 23.0274 23.1974 23.12 23.29L26 26.17L32.88 19.29C33.067 19.103 33.3206 18.998 33.585 18.998C33.8494 18.998 34.103 19.103 34.29 19.29C34.477 19.477 34.582 19.7306 34.582 19.995C34.582 20.2594 34.477 20.513 34.29 20.7L26.71 28.29Z"
              fill="#33445C"
            />
            <rect x="0.5" y="0.5" width="55" height="47" rx="11.5" stroke="#E5E8EB" />
          </svg>
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
        labelString="Analyzing resources available for books chosen, please be patient..."
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
            <ul>
              {#each lang0ResourceTypesAndNames as lang0ResourceTypeAndName, index}
                <label for="lang0-resourcetype-{index}">
                  <li class="target flex items-center py-2 pl-4">
                    <input
                      id="lang0-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$resourceTypesStore}
                      value={lang0ResourceTypeAndName}
                      class="checkbox-target checkbox-style"
                    />
                    <span class="pl-1 text-xl">{getResourceTypeName(lang0ResourceTypeAndName)}</span
                    >
                  </li>
                </label>
              {/each}
            </ul>
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
            <ul>
              {#each lang1ResourceTypesAndNames as lang1ResourceTypeAndName, index}
                <label for="lang1-resourcetype-{index}">
                  <li class="target flex items-center py-2 pl-4">
                    <input
                      id="lang1-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$resourceTypesStore}
                      value={lang1ResourceTypeAndName}
                      class="checkbox-target checkbox-style"
                    />
                    <span class="pl-1 text-xl">{getResourceTypeName(lang1ResourceTypeAndName)}</span
                    >
                  </li>
                </label>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    {:else}
      <div class="mb-2 flex flex-shrink-0 flex-grow-0 flex-row">
        {#if $langCountStore > 0}
          <div class="w-1/2">
            <h3 class="text-2xl text-[#33445C]">{$langNamesStore[0]}</h3>
          </div>
        {/if}
        {#if $langCountStore > 1 && lang1ResourceTypesAndNames}
          <div class="w-1/2">
            <h3 class="text-2xl text-[#33445C]">{$langNamesStore[1]}</h3>
          </div>
        {/if}
      </div>
      <div class="flex flex-shrink-0 flex-grow-0 flex-row">
        {#if lang0ResourceTypesAndNames && lang0ResourceTypesAndNames.length > 0}
          <div class="w-1/2">
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
            <ul>
              {#each lang0ResourceTypesAndNames as lang0ResourceTypeAndName, index}
                <label for="lang0-resourcetype-{index}">
                  <li class="target flex items-center py-2 pl-4">
                    <input
                      id="lang0-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$resourceTypesStore}
                      value={lang0ResourceTypeAndName}
                      class="checkbox-target checkbox-style"
                    />
                    <span class="pl-1">{getResourceTypeName(lang0ResourceTypeAndName)}</span>
                  </li>
                </label>
              {/each}
            </ul>
          </div>
        {/if}
        {#if lang1ResourceTypesAndNames && lang1ResourceTypesAndNames.length > 0}
          <div class="ml-4 w-1/2">
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
            <ul>
              {#each lang1ResourceTypesAndNames as lang1ResourceTypeAndName, index}
                <label for="lang1-resourcetype-{index}">
                  <li class="target flex items-center py-2 pl-4">
                    <input
                      id="lang1-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$resourceTypesStore}
                      value={lang1ResourceTypeAndName}
                      class="checkbox-target checkbox-style"
                    />
                    <span class="pl-1 text-xl">{getResourceTypeName(lang1ResourceTypeAndName)}</span
                    >
                  </li>
                </label>
              {/each}
            </ul>
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

<style global lang="postcss">
  li.target:has(input[type='checkbox']:checked) {
    background: #e6eefb;
  }
  input.checkbox-target[type='checkbox']:checked + span {
    color: #015ad9;
  }
  .checkbox-style {
    @apply h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600;
  }
</style>
