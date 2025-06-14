<script lang="ts">
  import { onMount } from 'svelte'
  import {
    PUBLIC_TAILWIND_SM_MIN_WIDTH,
    PUBLIC_BOOK_CODES_URL,
    PUBLIC_SHARED_BOOK_CODES_URL
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import WizardBreadcrumb from '$lib/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/WizardBasket.svelte'
  import otBooks from '$lib/ot-books'
  import { ntBookStore, otBookStore, bookCountStore } from '$lib/stores/BooksStore'
  import { langCodesStore, langCountStore } from '$lib/stores/LanguagesStore'
  import { getName, handleError } from '$lib/utils'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import MobileBookDisplay from './MobileBookDisplay.svelte'
  import DesktopBookDisplay from './DesktopBookDisplay.svelte'
  import Modal from '$lib/Modal.svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import { errorStore } from '$lib/stores/NotificationStore'
  import BlueSquareIcon from '$lib/BlueSquareIcon.svelte'
  import CheckIcon from '$lib/CheckIcon.svelte'
  import ErrorAlertIcon from '$lib/ErrorAlertIcon.svelte'
  import BlueSquareWithWhiteFillIcon from '../../lib/BlueSquareWithWhiteFillIcon.svelte'

  async function getBookCodesAndNames(
    langCode0: string,
    langCode1?: string,
    apiRootUrl: string = env.PUBLIC_BACKEND_API_URL,
    sharedBookCodesUrl: string = PUBLIC_SHARED_BOOK_CODES_URL,
    bookCodesUrl: string = PUBLIC_BOOK_CODES_URL
  ): Promise<Array<[string, string]>> {
    const url = langCode1
      ? `${apiRootUrl}${sharedBookCodesUrl}${langCode0}/${langCode1}`
      : `${apiRootUrl}${bookCodesUrl}${langCode0}`
    const response = await fetch(url)
    if (!response.ok) throw new Error(response.statusText)
    return response.json()
  }

  async function loadBookCodesAndNames() {
    try {
      const bookCodesAndNames = $langCountStore > 1
        ? await getBookCodesAndNames($langCodesStore[0], $langCodesStore[1])
        : await getBookCodesAndNames($langCodesStore[0])
      updateStores(bookCodesAndNames)
    } catch (err) {
      console.error(err)
      // Check the type of err
      $errorStore = handleError(err)
    }
  }

  let otBookCodes: Array<string>
  let ntBookCodes: Array<string>

  function updateStores(bookCodesAndNames: Array<[string, string]>) {
    otBookCodes = bookCodesAndNames
      .filter(([code]) => otBooks.includes(code))
      .map(([code, name]) => `${code}, ${name}`)
    if ($otBookStore.length > 0) {
      $otBookStore = $otBookStore.filter(item => otBookCodes.includes(item))
    }
    ntBookCodes = bookCodesAndNames
      .filter(([code]) => !otBooks.includes(code))
      .map(([code, name]) => `${code}, ${name}`)
    if ($ntBookStore.length > 0) {
      $ntBookStore = $ntBookStore.filter(item => ntBookCodes.includes(item))
    }
  }

  onMount(async () => {
   await loadBookCodesAndNames()
  })

  $: $bookCountStore = $otBookStore.length + $ntBookStore.length

  let otSearchTerm = ''
  let filteredOtBookCodes: Array<string> = []
  $: {
    if (otBookCodes) {
      filteredOtBookCodes = otBookCodes.filter((item) =>
        getName(item).toLowerCase().includes(otSearchTerm.toLowerCase())
      )
    }
  }
  let ntSearchTerm = ''
  let filteredNtBookCodes: Array<string> = []
  $: {
    if (ntBookCodes) {
      filteredNtBookCodes = ntBookCodes.filter((item) =>
        getName(item).toLowerCase().includes(ntSearchTerm.toLowerCase())
      )
    }
  }

  // If user has previously chosen (during this session, i.e., prior
  // to browser reload) any OT books and no NT books then default to
  // showing the OT, otherwise the default stands of showing the NT
  $: console.log(`$otBookStore.length: ${$otBookStore.length}`)
  $: console.log(`$ntBookStore.length: ${$ntBookStore.length}`)
  let showOldTestament = ($otBookStore.length > 0 && $ntBookStore.length === 0)
  let showFilterMenu = false
  let showWizardBasketModal = false

  let windowWidth: number = typeof window !== 'undefined' ? window.innerWidth : 0
  $: console.log(`windowWidth: ${windowWidth}`)

  let TAILWIND_SM_MIN_WIDTH: number = PUBLIC_TAILWIND_SM_MIN_WIDTH as unknown as number
  // $: console.log(`TAILWIND_SM_MIN_WIDTH: ${TAILWIND_SM_MIN_WIDTH}`)
</script>

<svelte:window bind:innerWidth={windowWidth} />

<WizardBreadcrumb />
<!-- container for "center" div -->
<div class="flex flex-grow flex-row overflow-y-auto overflow-x-hidden">
  <!-- center -->
  <div class="flex flex-1 flex-col bg-white sm:w-2/3">
    <h3
      class="ml-4 text-4xl font-normal leading-[48px]
               text-[#33445C]"
    >
      Select books
    </h3>
    <div class="ml-4 mt-2 flex items-center bg-white px-2 py-2">
      {#if !$errorStore && (!otBookCodes || !ntBookCodes)}
        <div class="ml-4">
          <ProgressIndicator
            labelString="Acquiring and analyzing books available for
                         languages chosen, please be patient as this
                         can take a few minutes"
          />
        </div>
      {:else}
        <div class="flex items-center">
          {#if showOldTestament}
            <label>
              <input
                id="filter-ot-books"
                type="search"
                bind:value={otSearchTerm}
                placeholder="Search OT books"
                class="search-style"
              />
            </label>
            <div class="ml-2 hidden sm:flex" role="group">
              <button
                class="h-10 w-36 rounded-l-md border-x-2
                              border-b-2 border-t-2 border-[#015ad9]
                              bg-[#015ad9] text-xl font-medium
                              leading-tight text-white transition duration-150 ease-in-out hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9]"
                on:click={() => (showOldTestament = true)}
              >
                Old Testament
              </button>
              <button
                class="h-10 w-36 rounded-r-md border-x-2 border-b-2
                       border-t-2 border-[#015ad9] bg-white text-xl font-medium leading-tight text-[#33445c] transition duration-150 ease-in-out hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white"
                on:click={() => (showOldTestament = false)}
              >
                New Testament
              </button>
            </div>
            <div class="ml-2 flex sm:hidden">
              <button on:click={() => (showFilterMenu = true)}>
                {#if showFilterMenu}
                  <BlueSquareWithWhiteFillIcon />
                {:else}
                  <BlueSquareIcon />
                {/if}
              </button>
              <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
                <div class="relative">
                  <CheckIcon />
                  {#if $langCountStore > 0 || $bookCountStore > 0}
                    <!-- badge -->
                    <div
                      class="bg-neutral-focus absolute -right-0.5 -top-0.5
                                h-7 w-7
                                rounded-full text-center text-xl text-[#33445C]"
                      style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                    >
                      <span
                        class="text-[8px]
                                    text-white">{$langCountStore + $bookCountStore}</span
                      >
                    </div>
                  {/if}
                </div>
              </button>
            </div>
            {#if showFilterMenu}
              <Modal title="Filter" bind:showFilterMenu>
                <svelte:fragment slot="body">
                  <label for="show-ot-radio-button">
                    <div
                      class="radio-target flex h-[48px]
                                items-center py-2 pl-4 pr-8"
                    >
                      <input
                        id="show-ot-radio-button"
                        type="radio"
                        value={true}
                        bind:group={showOldTestament}
                        class="radio-style"
                      />
                      <span class="pl-1 text-xl text-[#33445C]">Old Testament</span>
                    </div>
                  </label>
                  <label for="show-nt-radio-button">
                    <div
                      class="radio-target flex h-[48px]
                                items-center py-2 pl-4 pr-8"
                    >
                      <input
                        id="show-nt-radio-button"
                        type="radio"
                        value={false}
                        bind:group={showOldTestament}
                        class="radio-style"
                      />
                      <span class="pl-1 text-xl text-[#33445C]">New Testament</span>
                    </div>
                  </label>
                </svelte:fragment>
              </Modal>
            {/if}
          {:else}
            <label>
              <input
                id="filter-nt-books"
                type="search"
                bind:value={ntSearchTerm}
                placeholder="Search NT books"
                class="search-style"
              />
            </label>
            <div class="ml-2 hidden sm:flex" role="group">
              <button
                class="h-10 w-36 rounded-l-md border-x-2 border-x-2 border-b-2 border-t-2 border-[#015ad9] bg-white text-xl font-medium leading-tight text-[#33445c] transition duration-150 ease-in-out hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white"
                on:click={() => (showOldTestament = true)}
              >
                Old Testament
              </button>
              <button
                class="h-10 w-36 rounded-r-md border-b-2
                        border-r-2 border-t-2 border-[#015ad9] bg-[#015ad9] text-xl font-medium leading-tight text-white transition duration-150 ease-in-out hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8]"
                on:click={() => (showOldTestament = false)}
              >
                New Testament
              </button>
            </div>
            <div class="ml-2 flex sm:hidden">
              <button on:click={() => (showFilterMenu = true)}>
                {#if showFilterMenu}
                  <BlueSquareWithWhiteFillIcon />
                {:else}
                  <BlueSquareIcon />
                {/if}
              </button>
              <button class="ml-2" on:click={() => (showWizardBasketModal = true)}>
                <div class="relative">
                  <CheckIcon />
                  {#if $langCountStore > 0 || $bookCountStore > 0}
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
                                  text-white">{$langCountStore + $bookCountStore}</span
                      >
                    </div>
                  {/if}
                </div>
              </button>
            </div>
            {#if showFilterMenu}
              <Modal title="Filter" bind:showFilterMenu>
                <svelte:fragment slot="body">
                  <label for="show-gateway-radio-button">
                    <div
                      class="radio-target flex h-[48px]
                                items-center py-2 pl-4 pr-8"
                    >
                      <input
                        id="show-gateway-radio-button"
                        type="radio"
                        value={true}
                        bind:group={showOldTestament}
                        class="radio-style"
                      />
                      <span class="pl-1 text-xl text-[#33445C]">Old Testament</span>
                    </div>
                  </label>
                  <label for="show-heart-radio-button">
                    <div
                      class="radio-target flex h-[48px]
                                items-center py-2 pl-4 pr-8"
                    >
                      <input
                        id="show-heart-radio-button"
                        type="radio"
                        value={false}
                        bind:group={showOldTestament}
                        class="radio-style"
                      />
                      <span class="pl-1 text-xl text-[#33445C]">New Testament</span>
                    </div>
                  </label>
                </svelte:fragment>
              </Modal>
            {/if}
          {/if}
        </div>
      {/if}
    </div>

    {#if $errorStore}
      <div class="bg-white">
        <ErrorAlertIcon />
        <div class="m-auto"><h3 class="text-center text-[#B85659]">Uh Oh...</h3></div>
        <div class="m-auto">
          <p class="text-xl text-[#B3B9C2]">
            Something went wrong. Please review your selections or contact tech support for
            assistance.
          </p>
        </div>
      </div>
    {:else if $langCountStore > 0}
      {#if windowWidth < TAILWIND_SM_MIN_WIDTH}
        <MobileBookDisplay
          {showOldTestament}
          {otBookCodes}
          {ntBookCodes}
          {filteredOtBookCodes}
          {filteredNtBookCodes}
        />
      {:else}
        <DesktopBookDisplay
          {showOldTestament}
          {otBookCodes}
          {ntBookCodes}
          {filteredOtBookCodes}
          {filteredNtBookCodes}
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

<style global lang="postcss">
  #filter-ot-books,
  #filter-nt-books {
    text-indent: 17px;
    padding-left: 5px;
    background-image: url('data:image/svg+xml,<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M15.5014 14.0014H14.7114L14.4314 13.7314C15.0564 13.0054 15.5131 12.1502 15.769 11.2271C16.0248 10.3039 16.0735 9.33559 15.9114 8.39144C15.4414 5.61144 13.1214 3.39144 10.3214 3.05144C9.33706 2.92691 8.33723 3.02921 7.39846 3.35053C6.4597 3.67185 5.60688 4.20366 4.90527 4.90527C4.20366 5.60688 3.67185 6.4597 3.35053 7.39846C3.02921 8.33723 2.92691 9.33706 3.05144 10.3214C3.39144 13.1214 5.61144 15.4414 8.39144 15.9114C9.33559 16.0735 10.3039 16.0248 11.2271 15.769C12.1502 15.5131 13.0054 15.0564 13.7314 14.4314L14.0014 14.7114V15.5014L18.2514 19.7514C18.6614 20.1614 19.3314 20.1614 19.7414 19.7514C20.1514 19.3414 20.1514 18.6714 19.7414 18.2614L15.5014 14.0014ZM9.50144 14.0014C7.01144 14.0014 5.00144 11.9914 5.00144 9.50144C5.00144 7.01144 7.01144 5.00144 9.50144 5.00144C11.9914 5.00144 14.0014 7.01144 14.0014 9.50144C14.0014 11.9914 11.9914 14.0014 9.50144 14.0014Z" fill="%2366768B"/></svg>');
    background-repeat: no-repeat;
    background-position: left center;
    outline: 0;
  }
  div.target:has(input[type='checkbox']:checked) {
    background: #e6eefb;
  }
  div.target:has(input[type='radio']:checked) {
    background: #e6eefb;
  }
  input.checkbox-target[type='checkbox']:checked + span {
    color: #015ad9;
  }
  div.target3:has(input[type='checkbox']:checked) + span {
    color: #015ad9;
  }
  div.target2:has(input[type='checkbox']:checked) + div {
    color: #015ad9;
  }
  .checkbox-style {
    @apply h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600;
  }
  .radio-style {
    @apply h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600;
  }
  .search-style {
    @apply h-full w-full rounded-[7px] border border-gray-200 bg-transparent px-3 py-2.5 font-sans text-xl  font-normal text-[#33445c] outline outline-0 transition-all focus:border-2 focus:border-gray-900 focus:outline-0;
  }
</style>
