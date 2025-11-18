<script lang="ts">
  import WizardBreadcrumb from '$lib/stet/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/stet/WizardBasket.svelte'
  import WizardBasketModal from '$lib/WizardBasketModal.svelte'
  import { emailStore, documentRequestKeyStore } from '$lib/stet/stores/SettingsStore'
  import { documentReadyStore, errorStore } from '$lib/stet/stores/NotificationStore'
  import { langCountStore } from '$lib/stet/stores/LanguagesStore'
  import GenerateDocument from './GenerateDocument.svelte'
  import LogRocket from 'logrocket'
  import CheckIcon from '$lib/CheckIcon.svelte'

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
          {#if $langCountStore}
            <!-- badge -->
            <div
              class="bg-neutral-focus absolute -right-0.5 -top-0.5
                        h-7 w-7
                        rounded-full text-center text-[#33445C]"
              style="background: linear-gradient(180deg, #1876FD 0%, #015AD9 100%);"
            >
              <span class="text-[8px] text-white">{$langCountStore}</span>
            </div>
          {/if}
        </div>
      </button>
    </div>
    <!-- main content -->
    <main class="flex-1 overflow-y-auto p-4">
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
