<script lang="ts">
  import Modal from '$lib/Modal.svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import { langCountStore } from '$lib/stores/LanguagesStore'
  import BlueSquareIcon from '$lib/BlueSquareIcon.svelte'
  import BlueSquareWithWhiteFillIcon from '$lib/BlueSquareWithWhiteFillIcon.svelte'
  import CheckIcon from '$lib/CheckIcon.svelte'

  function selectGatewayTab() {
    showGatewayLanguages = true
  }

  function selectHeartTab() {
    showGatewayLanguages = false
  }

  export let langCodeNameAndTypes: Array<[string, string, boolean]>
  export let showGatewayLanguages: boolean
  export let gatewaySearchTerm: string
  export let showFilterMenu: boolean
  export let showWizardBasketModal: boolean
  export let heartSearchTerm: string
</script>

<div class="ml-4 mt-2 flex items-center bg-white px-2 py-2">
  {#if !langCodeNameAndTypes || langCodeNameAndTypes.length === 0}
    <div class="ml-4">
      <ProgressIndicator />
    </div>
  {:else}
    <div class="flex items-center">
      {#if showGatewayLanguages}
        <label id="label-for-filter-gl-langs" for="filter-gl-langs">
          <input
            id="filter-gl-langs"
            type="search"
            bind:value={gatewaySearchTerm}
            placeholder="Search Gateway Languages"
            class="search-style"
          />
        </label>
        <div class="ml-2 hidden sm:flex" role="group">
          <button
            class="h-10 w-36 rounded-l-md border-x-2 border-b-2
                    border-t-2 border-[#015ad9] bg-[#015ad9] text-xl font-medium leading-tight text-white transition duration-150 ease-in-out hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#015ad9]"
            on:click={selectGatewayTab}
          >
            Gateway
          </button>
          <button
            class="h-10 w-36 rounded-r-md border-b-2 border-r-2
                    border-t-2 border-[#015ad9] bg-white text-xl font-medium leading-tight text-[#33445C] transition duration-150 ease-in-out hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white"
            on:click={selectHeartTab}
          >
            Heart
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
              {#if $langCountStore > 0}
                <!-- badge -->
                <div
                  class="bg-neutral-focus absolute -right-0.5 -top-0.5
                        h-7 w-7
                        rounded-full
                        text-center text-xl text-[#33445C]"
                  style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                >
                  <span class="text-[8px] text-white">{$langCountStore}</span>
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
                    bind:group={showGatewayLanguages}
                    class="radio-style"
                  />
                  <span class="pl-1 text-xl text-[#33445C]">Gateway languages</span>
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
                    bind:group={showGatewayLanguages}
                    class="radio-style"
                  />
                  <span class="pl-1 text-xl text-[#33445C]">Heart languages</span>
                </div>
              </label>
            </svelte:fragment>
          </Modal>
        {/if}
      {:else}
        <label id="label-for-filter-non-gl-langs" for="filter-non-gl-langs">
          <input
            id="filter-non-gl-langs"
            type="search"
            bind:value={heartSearchTerm}
            class="search-style"
            placeholder="Search Heart Languages"
          />
        </label>
        <div class="ml-2 hidden sm:flex" role="group">
          <button
            class="h-10 w-36 rounded-l-md border-x-2 border-b-2
                    border-t-2 border-[#015ad9] bg-white text-xl font-medium leading-tight text-[#33445c] transition duration-150 ease-in-out hover:bg-white focus:bg-white focus:outline-none focus:ring-0 active:bg-white"
            on:click={selectGatewayTab}
          >
            Gateway
          </button>
          <button
            class="h-10 w-36 rounded-r-md border-b-2
                    border-r-2 border-t-2 border-[#015ad9] bg-[#015ad9] text-xl font-medium leading-tight text-white transition duration-150 ease-in-out hover:bg-[#015ad9] focus:bg-[#015ad9] focus:outline-none focus:ring-0 active:bg-[#feeed8]"
            on:click={selectHeartTab}
          >
            Heart
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
              {#if $langCountStore > 0}
                <!-- badge -->
                <div
                  class="bg-neutral-focus absolute -right-0.5 -top-0.5
                        h-7 w-7
                        rounded-full
                        text-center text-xl text-[#33445C]"
                  style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
                >
                  <span class="text-[8px] text-white">{$langCountStore}</span>
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
                    bind:group={showGatewayLanguages}
                    class="radio-style"
                  />
                  <span class="pl-1 text-xl text-[#33445C]">Gateway languages</span>
                </div>
              </label>
              <label for="show-heart-radio-button">
                <div
                  class="radio-target flex h-[48px]
                          items-center px-4 py-2"
                >
                  <input
                    id="show-heart-radio-button"
                    type="radio"
                    value={false}
                    bind:group={showGatewayLanguages}
                    class="radio-style"
                  />
                  <span class="pl-1 text-xl text-[#33445C]">Heart languages</span>
                </div>
              </label>
            </svelte:fragment>
          </Modal>
        {/if}
      {/if}
    </div>
  {/if}
</div>

<style global lang="postcss">
  .search-style {
    @apply h-full w-full rounded-[7px] border border-blue-500 bg-transparent px-3 py-2.5 font-sans text-xl  font-normal text-[#33445c] outline outline-0 transition-all focus:ring focus:ring-indigo-200 focus:border-2 focus:border-indigo-600;
  }
</style>
