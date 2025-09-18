<script lang="ts">
  import CloseIcon from '$lib/CloseIcon.svelte'

  export let showWizardBasketModal = false
  export let title = ''
  let dialog: HTMLDialogElement

  $: if (dialog && showWizardBasketModal) dialog.showModal()
</script>

<!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
<dialog
  bind:this={dialog}
  on:close={() => (showWizardBasketModal = false)}
  on:click|self={() => dialog.close()}
  id="dialog-container"
  class="fixed z-50 h-full w-full overflow-y-auto overflow-x-hidden outline-none rounded-lg bg-[#f2f3f5]"
  tabindex="-1"
>
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div
    on:click|stopPropagation
    class="pointer-events-none relative mx-auto my-6 w-auto max-w-lg sm:h-[calc(100%-3rem)]"
  >
    <div
      class="pointer-events-auto relative flex w-full max-h-full
                flex-col overflow-y-auto border-none bg-[#f2f3f5] text-current outline-none"
    >
      <div
        class="flex flex-shrink-0 items-center justify-between bg-[#f2f3f5] border-b border-[#e5e8eb] p-4"
      >
        <h5 class="text-xl font-bold text-[#33445C]">{title}</h5>
        <button autofocus on:click={() => dialog.close()}>
          <CloseIcon />
        </button>
      </div>
      <div class="relative flex-auto overflow-y-auto">
        <slot name="body" />
      </div>
      <div class="flex flex-shrink-0 flex-wrap items-center order-t border-[#e5e8eb] p-4">
        <!-- svelte-ignore a11y-autofocus -->
        <button
          class="h-[48px] w-[115px] rounded-md border-2
                       border-[#e5e8eb] bg-white font-medium
                       leading-tight text-[#33445C] text-xl transition
                       duration-150 ease-in-out"
          on:click={() => dialog.close()}
        >
          <div class="flex items-center">
            <span class="ml-2"><CloseIcon /></span>
            <span class="ml-2">Close</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</dialog>

<style>
  #dialog-container {
    box-shadow: 0px 6px 6px 0px #0015333b;

    box-shadow: 0px 10px 20px 0px #00153330;
  }
</style>
