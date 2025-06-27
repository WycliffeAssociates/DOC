<script lang="ts">
  import type { SelectElement } from './types'
  import Switch from './Switch.svelte'
  import WizardBreadcrumb from '$lib/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/WizardBasket.svelte'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    assemblyStrategyChunkSizeStore,
    docTypeStore,
    emailStore,
    documentRequestKeyStore,
    settingsUpdated,
    useChapterLabelsStore
  } from '$lib/stores/SettingsStore'
  import { documentReadyStore, errorStore } from '$lib/stores/NotificationStore'
  import {
    limitTwStore,
    resourceTypesStore,
    resourceTypesCountStore,
    twResourceRequestedStore,
    usfmAvailableStore
  } from '$lib/stores/ResourceTypesStore'
  import { langCodesStore, langCountStore } from '$lib/stores/LanguagesStore'
  import { bookCountStore } from '$lib/stores/BooksStore'
  import GenerateDocument from './GenerateDocument.svelte'
  import LogRocket from 'logrocket'
  import CheckIcon from '$lib/CheckIcon.svelte'

  let showAdvanced = false // Show optional/advanced settings flag

  let chapter: SelectElement = {
    id: 'chapter',
    label: <string>import.meta.env.VITE_CHUNK_SIZE_CHAPTER
  }
  // Set default value of chapter
  $assemblyStrategyChunkSizeStore = chapter.id

  // The 3rd party HTML to PDF conversion library we use, weasyprint,
  // doesn't seem to be able to handle line length for the Khmer language
  // which results in words overlapping each other when two column
  // layout of Khmer content is displayed. Only TN and TQ resource types
  // use two column layout and thus if those are selected by the user
  // then the UI will exclude PDF as an output format choice for
  // Khmer.
  let kmRegexp = new RegExp('km, tn, .*|km, tq, .*')
  let showPdfAsOption: boolean = true
  // $: console.log(`showPdfAsOption: ${showPdfAsOption}`)
  $: {
    if ($resourceTypesStore) {
      if ($resourceTypesStore.some((item) => kmRegexp.test(item))) {
        showPdfAsOption = false
      }
    }
  }

  $: showEmail = false
  $: showEmailCaptured = false
  $: $documentReadyStore = false

  if ($emailStore && $emailStore === '') {
    $emailStore = null
    LogRocket.identify($documentRequestKeyStore)
  } else if ($emailStore === undefined) {
    $emailStore = null
    LogRocket.identify($documentRequestKeyStore)
  } else if ($emailStore && $emailStore !== '') {
    $emailStore = $emailStore.trim()
    // LogRocket init call happens in App.svelte.
    // Tell LogRocket to identify the session via the email provided.
    LogRocket.identify($emailStore)
  }

  let showWizardBasketModal = false
</script>

<WizardBreadcrumb />

<!-- container for "center" div -->
<div class="flex-grow flex flex-row overflow-hidden">
  <!-- center -->
  <div class="flex-1 flex flex-col sm:w-2/3 bg-white mx-4 mb-6">
    <h3 class="bg-white text-[#33445C] text-4xl font-normal leading-[48px] mb-4">
      Generate document
    </h3>

    <!-- mobile basket modal launcher -->
    <div class="sm:hidden text-right mr-4">
      <button on:click={() => (showWizardBasketModal = true)}>
        <div class="relative">
          <CheckIcon />
          {#if $langCountStore > 0 || $bookCountStore > 0 || $resourceTypesCountStore > 0}
            <!-- badge -->
            <div
              class="text-center absolute -top-0.5 -right-0.5
                        bg-neutral-focus text-[#33445C]
                        rounded-full w-7 h-7"
              style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
            >
              <span class="text-[8px] text-white"
                >{$langCountStore + $bookCountStore + $resourceTypesCountStore}</span
              >
            </div>
          {/if}
        </div>
      </button>
    </div>
    <!-- main content -->
    <main class="flex-1 overflow-y-auto p-4">
      <h3 class="mb-2 mt-2 text-2xl text-[#33445C]">File type</h3>
      <div class="ml-4">
        <div class="mb-2">
          <label>
            <input
              name="docType"
              value={'docx'}
              bind:group={$docTypeStore}
              type="radio"
              on:change={() => {
                $settingsUpdated = true
                $errorStore = ''
              }}
              class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
            />
            <span class="text-xl text-[#33445C]">Docx</span>
          </label>
        </div>
        <div class="mb-2">
          <label>
            <input
              name="docType"
              value={'epub'}
              bind:group={$docTypeStore}
              type="radio"
              on:change={() => {
                $settingsUpdated = true
                $errorStore = ''
              }}
              class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
            />
            <span class="text-xl text-[#33445C]">ePub</span>
          </label>
        </div>
        {#if showPdfAsOption}
          <div class="mb-2">
            <label>
              <input
                name="docType"
                value={'pdf'}
                bind:group={$docTypeStore}
                type="radio"
                on:change={() => {
                  $settingsUpdated = true
                  $errorStore = ''
                }}
                class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
              />
              <span class="text-xl text-[#33445C]">PDF</span>
            </label>
          </div>
        {/if}
      </div>
      <h3 class="mb-2 mt-4 text-2xl text-[#33445C]">Layout</h3>
      <div class="ml-4">
        {#if $langCodesStore[1]}
          <div class="mb-2">
            <label>
              <input
                name="assemblyType"
                value={'lbo'}
                bind:group={$assemblyStrategyKindStore}
                type="radio"
                on:change={() => {
                  $settingsUpdated = true
                  $errorStore = ''
                }}
                class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
              />
              <span class="text-xl text-[#33445C]">Interleave content by book</span>
            </label>
          </div>
          <div class="mb-6">
            <label>
              <input
                name="assemblyType"
                value={'blo'}
                bind:group={$assemblyStrategyKindStore}
                type="radio"
                on:change={() => {
                  $settingsUpdated = true
                  $errorStore = ''
                }}
                class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
              />
              <span class="text-xl text-[#33445C]">Interleave content by chapter</span>
            </label>
          </div>
        {/if}
        <div class="flex">
          <Switch bind:checked={$layoutForPrintStore} id="layout-for-print-store" />
          <span class="ml-2 text-xl text-[#33445C]">Print optimization</span>
        </div>
        <div class="mt-2">
          <span class="text-lg text-[#33445C]"
            >Enabling this option will remove extra whitespace</span
          >
        </div>
        {#if $twResourceRequestedStore && $usfmAvailableStore}
          <div class="mb-2 mt-6 flex">
            <Switch bind:checked={$limitTwStore} id="limit-tw-store" />
            <span class="ml-2 text-xl text-[#33445C]">Limit TW words</span>
          </div>
          <div>
            <span class="text-lg text-[#33445C]"
              >Enabling this option will filter TW words down to only those that occur in the
              scripture for the books chosen</span
            >
          </div>
        {/if}
      </div>
      <button
        class="mb-4 mt-2 w-1/2 rounded-md
                    border border-[#E5E8EB] bg-[#F2F3F5] p-4
                    text-center text-xl text-[#B3B9C2] transition hover:bg-[#efefef]"
        on:click={() => (showAdvanced = !showAdvanced)}
      >
        {showAdvanced ? '▼ Hide Optional Settings' : '▶ Show Optional Settings'}
      </button>
      {#if showAdvanced}
        <h3 class="mb-2 mt-2 text-2xl text-[#33445C]">Optional Settings</h3>
        <div class="ml-4">
          <div class="mb-2 mt-6 flex">
            <Switch bind:checked={$useChapterLabelsStore} id="use-chapter-labels" />
            <span class="ml-2 text-xl text-[#33445C]"
              >Use chapter labels, e.g., 'Chapter 1' instead of '1'</span
            >
          </div>
        </div>
      {/if}
      <h3 class="mb-2 mt-4 text-2xl text-[#33445C]">Notification</h3>
      <div class="ml-4">
        {#if !$documentReadyStore}
          <div>
            <input
              id="emailCheckbox"
              type="checkbox"
              on:click={() => (showEmail = !showEmail)}
              value={showEmail}
              class="checkbox-target checkbox-style"
            />
            <label for="emailCheckbox" class="pl-1 text-xl text-[#33445C]"
              >Email me a copy of my document.</label
            >
          </div>
        {/if}
        {#if showEmail && !showEmailCaptured}
          <div>
            <label for="email" class="pl-1 text-xl text-[#33445C]">Email address</label>
          </div>
          <input
            type="text"
            name="email"
            id="email"
            bind:value={$emailStore}
            placeholder="Type email address here (optional)"
            class="input input-bordered w-full max-w-xs bg-white"
          />
          <div>
            <button
              class="mt-4 rounded-md bg-[#E6EEFB] px-8 py-4
                           text-xl text-[#015AD9]"
              on:click={() => (showEmailCaptured = true)}>Submit</button
            >
          </div>
        {/if}
        {#if showEmailCaptured}
          <div class="text-xl text-[#33445C]">
            A copy of your file will be sent to {$emailStore} when it is ready.
          </div>
        {/if}
      </div>

      <GenerateDocument />
    </main>
  </div>

  <!-- isMobile -->
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
