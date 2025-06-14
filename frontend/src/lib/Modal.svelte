<script lang="ts">
  import CloseIcon from '$lib/CloseIcon.svelte'

  export let showFilterMenu = false
  export let title = ''
  let dialog: HTMLDialogElement
  $: if (dialog && showFilterMenu) dialog.showModal()
</script>

<!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
<dialog
  bind:this={dialog}
  on:close={() => (showFilterMenu = false)}
  on:click|self={() => dialog.close()}
  id="dialog-container"
  class="fixed pin z-50 overflow-y-auto bg-smoke-light flex rounded-lg shadow-xl"
>
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div
    on:click|stopPropagation
    class="relative bg-white w-full max-w-md
              m-auto flex-col flex border-2
              border-[#e5e8eb] rounded-lg shadow-xl"
  >
    <h3 class="font-bold text-xl text-[#33445C] ml-4 mt-4">{title}</h3>
    <div class="content">
      <slot name="body" />
    </div>
    <div class="mt-4">
      <!-- svelte-ignore a11y-autofocus -->
      <button
        autofocus
        class="rounded-md w-[115px] h-[48px] ml-4 mb-4 bg-white text-[#33445C]
                     text-xl font-medium leading-tight border-2
                     border-[#e5e8eb] transition
                     duration-150 ease-in-out"
        on:click={() => dialog.close()}
      >
        <div class="flex items-center">
          <CloseIcon />
          <span class="ml-2">Close</span>
        </div>
      </button>
    </div>
  </div>
</dialog>

<style>
  #dialog-container {
    box-shadow: 0px 6px 6px 0px #0015333b;

    box-shadow: 0px 10px 20px 0px #00153330;
  }
  dialog::backdrop {
    background: rgba(0, 0, 0, 0.3);
  }
  dialog[open] {
    animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  @keyframes zoom {
    from {
      transform: scale(0.95);
    }
    to {
      transform: scale(1);
    }
  }
  dialog[open]::backdrop {
    animation: fade 0.2s ease-out;
  }
  @keyframes fade {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
</style>
