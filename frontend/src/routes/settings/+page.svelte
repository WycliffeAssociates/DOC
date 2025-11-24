<script lang="ts">
  import type { SelectElement } from './types'
  import Switch from '$lib/Switch.svelte'
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
    settingsUpdatedStore,
    showTnBookIntroStore,
    showTnChapterIntroStore,
    showBcBookIntroStore,
    showBcChapterCommentaryStore,
    showRgChapterCommentaryStore,
    useChapterLabelsStore,
    useSectionVisualSeparatorStore,
    usePrinceStore,
    useTwoColumnLayoutForTnNotesStore,
    useTwoColumnLayoutForTqNotesStore
  } from '$lib/stores/SettingsStore'
  import { documentReadyStore, errorStore } from '$lib/stores/NotificationStore'
  import {
    // limitTwStore,
    resourceTypesStore,
    resourceTypesCountStore
    // twResourceRequestedStore,
    // usfmAvailableStore
  } from '$lib/stores/ResourceTypesStore'
  import { langCodesStore, langCountStore } from '$lib/stores/LanguagesStore'
  import { bookCountStore } from '$lib/stores/BooksStore'
  import GenerateDocument from './GenerateDocument.svelte'
  import LogRocket from 'logrocket'
  import CheckIcon from '$lib/CheckIcon.svelte'
  import OneColumnLayoutIcon from '$lib/OneColumnLayoutIcon.svelte'
  import TwoColumnLayoutIcon from '$lib/TwoColumnLayoutIcon.svelte'

  let showAdvanced = false // Show optional/advanced settings flag

  let chapter: SelectElement = {
    id: 'chapter',
    label: <string>import.meta.env.VITE_CHUNK_SIZE_CHAPTER
  }
  // Set default value of chapter
  $assemblyStrategyChunkSizeStore = chapter.id

  // Only show optional settings that are relevant to the resources
  // the user has chosen.
  let usfmRegex = new RegExp(
    'avd,.*|ayt,.*|blv,.*|cuv,.*|f10,.*|nav,.*|reg,.*|ugnt,.*|uhb,.*|ulb,.*|usfm,.*'
  )
  let tnRegex = new RegExp('tn, .*')
  let tqRegex = new RegExp('tq, .*')
  let bcRegex = new RegExp('bc, .*')
  let rgRegex = new RegExp('rg, .*')
  let showUsfmSettingsAsOption: boolean = false
  let showTnTwoColAsOption: boolean = false
  let showTqTwoColAsOption: boolean = false
  let showTnBookIntroAsOption: boolean = false
  let showBcBookIntroAsOption: boolean = false
  let showTnChapterIntroAsOption: boolean = false
  let showBcChapterCommentaryAsOption: boolean = false
  let showRgChapterCommentaryAsOption: boolean = false
  $: {
    if ($resourceTypesStore) {
      if ($resourceTypesStore.some((item) => usfmRegex.test(item))) {
        showUsfmSettingsAsOption = true
      }
      if ($resourceTypesStore.some((item) => tnRegex.test(item))) {
        showTnTwoColAsOption = true
        showTnBookIntroAsOption = true
        showTnChapterIntroAsOption = true
      }
      if ($resourceTypesStore.some((item) => tqRegex.test(item))) {
        showTqTwoColAsOption = true
      }
      if ($resourceTypesStore.some((item) => bcRegex.test(item))) {
        showBcBookIntroAsOption = true
        showBcChapterCommentaryAsOption = true
      }
      if ($resourceTypesStore.some((item) => rgRegex.test(item))) {
        showRgChapterCommentaryAsOption = true
      }
    }
  }
  $: console.log(`resourceTypesStore: ${$resourceTypesStore}`)

  // If user chooses versification, they probably don't want to see
  // the verbose parts of TN, BC, and RG resources by default. They can
  // choose to include them via UI switches if they have chosen such resources
  // to begin with.
  // This variable is used to track user interacting with optional
  // settings that would impact versification output.
  let userInteracted = false
  $: {
    if (
      !userInteracted &&
      ($assemblyStrategyKindStore === 'lvo' || $assemblyStrategyKindStore === 'bvo')
    ) {
      $showTnBookIntroStore = false
      $showBcBookIntroStore = false
      $showTnChapterIntroStore = false
      $showBcChapterCommentaryStore = false
      $showRgChapterCommentaryStore = false
    }
  }
  //  Make sure if the user first chooses one of the versification
  // assembly strategies and then subsequently chooses one of the non-versification
  // strategies, the appropriate defaults for non-versification are
  // chosen.
  $: {
    if (
      $settingsUpdatedStore &&
      $assemblyStrategyKindStore !== 'lvo' &&
      $assemblyStrategyKindStore !== 'bvo'
    ) {
      $showTnBookIntroStore = true
      $showBcBookIntroStore = true
      $showTnChapterIntroStore = true
      $showBcChapterCommentaryStore = true
      $showRgChapterCommentaryStore = true
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
<div class="flex flex-grow flex-row overflow-hidden">
  <!-- center -->
  <div class="mx-4 mb-6 flex flex-1 flex-col bg-white sm:w-2/3">
    <h3 class="mb-4 bg-white text-4xl font-normal leading-[48px] text-[#33445C]">
      Generate document
    </h3>

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
                        rounded-full text-center text-[#33445C]"
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
                $settingsUpdatedStore = true
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
                $settingsUpdatedStore = true
                $errorStore = ''
              }}
              class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
            />
            <span class="text-xl text-[#33445C]">ePub</span>
          </label>
        </div>
        <div class="mb-2">
          <label>
            <input
              name="docType"
              value={'pdf'}
              bind:group={$docTypeStore}
              type="radio"
              on:change={() => {
                $settingsUpdatedStore = true
                $errorStore = ''
              }}
              class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
            />
            <span class="text-xl text-[#33445C]">PDF</span>
          </label>
        </div>
        {#if $docTypeStore === 'pdf'}
          <div class="mb-2 mt-6 flex">
            <Switch bind:checked={$usePrinceStore} id="use-prince" />
            <span class="ml-2 text-xl text-[#33445C]"
              >Use <a
                class="text-blue-600 visited:text-purple-600"
                href="https://www.princexml.com"
                target="_blank">PrinceXml</a
              > to produce the PDF (much faster and better quality, but with Prince's 'P' logo at top
              right of first page of PDF)</span
            >
          </div>
        {/if}
      </div>
      <h3 class="mb-2 mt-4 text-2xl text-[#33445C]">Layout</h3>
      <div class="ml-4">
        <div class="mb-2">
          <label>
            <input
              name="assemblyType"
              value={'lbo'}
              bind:group={$assemblyStrategyKindStore}
              type="radio"
              on:change={() => {
                $settingsUpdatedStore = true
                $errorStore = ''
              }}
              class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
            />
            <span class="text-xl text-[#33445C]">Interleave content by book</span>
          </label>
        </div>
        {#if showUsfmSettingsAsOption}
          <div class="mb-2">
            <label>
              <input
                name="assemblyType"
                value={'lvo'}
                bind:group={$assemblyStrategyKindStore}
                type="radio"
                on:change={() => {
                  $settingsUpdatedStore = true
                  $errorStore = ''
                }}
                class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
              />
              <span class="text-xl text-[#33445C]"
                >Interleave content by verse one book at a time</span
              >
            </label>
          </div>
        {/if}
        {#if $langCodesStore[1]}
          <div class="mb-2">
            <label>
              <input
                name="assemblyType"
                value={'blo'}
                bind:group={$assemblyStrategyKindStore}
                type="radio"
                on:change={() => {
                  $settingsUpdatedStore = true
                  $errorStore = ''
                }}
                class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
              />
              <span class="text-xl text-[#33445C]">Interleave content by chapter</span>
            </label>
          </div>
          {#if showUsfmSettingsAsOption}
            <div class="mb-6">
              <label>
                <input
                  name="assemblyType"
                  value={'bvo'}
                  bind:group={$assemblyStrategyKindStore}
                  type="radio"
                  on:change={() => {
                    $settingsUpdatedStore = true
                    $errorStore = ''
                  }}
                  class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600"
                />
                <span class="text-xl text-[#33445C]"
                  >Interleave content by verse one chapter at a time</span
                >
              </label>
            </div>
          {/if}
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
        <!-- {#if $twResourceRequestedStore && $usfmAvailableStore} -->
        <!--   <div class="mb-2 mt-6 flex"> -->
        <!--     <Switch bind:checked={$limitTwStore} id="limit-tw-store" /> -->
        <!--     <span class="ml-2 text-xl text-[#33445C]">Limit TW words</span> -->
        <!--   </div> -->
        <!--   <div> -->
        <!--     <span class="text-lg text-[#33445C]" -->
        <!--       >Enabling this option will filter TW words down to only those that occur in the -->
        <!--       scripture for the books chosen</span -->
        <!--     > -->
        <!--   </div> -->
        <!-- {/if} -->
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
          {#if showUsfmSettingsAsOption}
            <div class="mb-2 mt-6 flex">
              <Switch bind:checked={$useChapterLabelsStore} id="use-chapter-labels" />
              <span class="ml-2 text-xl text-[#33445C]"
                >Use chapter labels, e.g., 'Chapter 1' instead of '1'</span
              >
            </div>
          {/if}
          <div class="mb-2 mt-6 flex">
            <Switch
              bind:checked={$useSectionVisualSeparatorStore}
              id="use-section-visual-separator"
            />
            <span class="ml-2 text-xl text-[#33445C]"
              >Show visual separator (horizontal line) between sections</span
            >
          </div>
          {#if $assemblyStrategyKindStore !== 'lvo' && $assemblyStrategyKindStore !== 'bvo' && showTnTwoColAsOption}
            <div class="mb-2 mt-6 flex items-center">
              <Switch
                bind:checked={$useTwoColumnLayoutForTnNotesStore}
                id="use-two-column-layout-for-tn"
              />
              {#if $useTwoColumnLayoutForTnNotesStore}
                <span class="ml-2 text-xl text-[#33445C]">Translation notes layout:</span>
                <TwoColumnLayoutIcon />
                <div
                  class="tooltip tooltip-info"
                  data-tip="This setting controls non-intro TN content
                  layout. A few
                                                            languages,
                                                            e.g.,
                                                            Khmer,
                                                            don't
                                                            render
                                                            well in
                                                            two
                                                            columns."
                >
                  ℹ️
                </div>
              {:else}
                <span class="ml-2 text-xl text-[#33445C]">Translation notes layout:</span>
                <OneColumnLayoutIcon />
                <div
                  class="tooltip tooltip-info"
                  data-tip="This setting controls non-intro TN content
                  layout. A few
                                                            languages,
                                                            e.g.,
                                                            Khmer,
                                                            don't
                                                            render
                                                            well in
                                                            two
                                                            columns."
                >
                  ℹ️
                </div>
              {/if}
            </div>
          {/if}
          {#if $assemblyStrategyKindStore !== 'lvo' && $assemblyStrategyKindStore !== 'bvo' && showTqTwoColAsOption}
            <div class="mb-2 mt-6 flex items-center">
              <Switch
                bind:checked={$useTwoColumnLayoutForTqNotesStore}
                id="use-two-column-layout-for-tq"
              />
              {#if $useTwoColumnLayoutForTqNotesStore}
                <span class="ml-2 text-xl text-[#33445C]">Translation questions layout:</span>
                <TwoColumnLayoutIcon />
                <div
                  class="tooltip tooltip-info"
                  data-tip="A few
                                                            languages,
                                                            e.g.,
                                                            Khmer,
                                                            don't
                                                            render
                                                            well in
                                                            two
                                                            columns."
                >
                  ℹ️
                </div>
              {:else}
                <span class="ml-2 text-xl text-[#33445C]">Translation questions layout:</span>
                <OneColumnLayoutIcon />
                <div
                  class="tooltip tooltip-info"
                  data-tip="A few
                                                            languages,
                                                            e.g.,
                                                            Khmer,
                                                            don't
                                                            render
                                                            well in
                                                            two
                                                            columns."
                >
                  ℹ️
                </div>
              {/if}
            </div>
          {/if}
          {#if showTnBookIntroAsOption}
            <div class="mb-2 mt-6 flex items-center">
              <Switch
                bind:checked={$showTnBookIntroStore}
                id="show-tn-book-intro"
                on:change={() => {
                  userInteracted = true
                }}
              />
              <span class="ml-2 text-xl text-[#33445C]">Include TN book intro</span>
            </div>
          {/if}
          {#if showBcBookIntroAsOption}
            <div class="mb-2 mt-6 flex items-center">
              <Switch bind:checked={$showBcBookIntroStore} id="show-bc-book-intro" />
              <span class="ml-2 text-xl text-[#33445C]">Include BC book intro</span>
            </div>
          {/if}
          {#if showTnBookIntroAsOption}
            <div class="mb-2 mt-6 flex items-center">
              <Switch bind:checked={$showTnChapterIntroStore} id="show-tn-chapter-intro" />
              <span class="ml-2 text-xl text-[#33445C]">Include TN chapter intro</span>
            </div>
          {/if}
          {#if showBcBookIntroAsOption}
            {#if $assemblyStrategyKindStore === 'lvo' || $assemblyStrategyKindStore === 'bvo'}
              <div class="mb-2 mt-6 flex items-center">
                <Switch
                  bind:checked={$showBcChapterCommentaryStore}
                  id="show-bc-chapter-commentary"
                />
                <span class="ml-2 text-xl text-[#33445C]">Include BC chapter commentary</span>
              </div>
            {/if}
          {/if}
          {#if showRgChapterCommentaryAsOption && ($assemblyStrategyKindStore === 'lvo' || $assemblyStrategyKindStore === 'bvo')}
            <div class="mb-2 mt-6 flex items-center">
              <Switch
                bind:checked={$showRgChapterCommentaryStore}
                id="show-rg-chapter-commentary"
              />
              <span class="ml-2 text-xl text-[#33445C]">Include RG chapter commentary</span>
            </div>
          {/if}
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
