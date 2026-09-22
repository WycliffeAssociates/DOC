<script lang="ts">
  import { settingsUpdatedStore } from '$lib/stet/stores/SettingsStore'
  import { errorStore } from '$lib/stet/stores/NotificationStore'
  export let id = ''
  export let checked = false
  export let disabled = false
</script>

<label for={id}>
  <div class="switch">
    <input
      {id}
      name={id}
      type="checkbox"
      class="sr-only"
      {disabled}
      bind:checked
      on:change={() => {
        $settingsUpdatedStore = true
        $errorStore = ''
      }}
    />
    <div class="track" />
    <div class="thumb" />
  </div>
</label>

<style global lang="postcss">
  .switch {
    @apply relative inline-block cursor-pointer select-none bg-transparent align-middle;
  }
  .track {
    @apply h-7 w-11 rounded-full border border-[#343434] bg-white shadow-inner;
  }
  .thumb {
    @apply absolute left-1 top-1 h-5 w-5 rounded-full bg-[#343434] transition-all duration-300 ease-in-out;
  }
  input[type='checkbox']:checked ~ .thumb {
    @apply translate-x-4 transform;
  }
  input[type='checkbox']:checked ~ .track {
    @apply transform transition-colors;
    background:
      linear-gradient(180deg, #1876fd 0%, #015ad9 100%), linear-gradient(0deg, #343434, #343434);
  }
  input[type='checkbox']:disabled ~ .track {
    @apply bg-gray-500;
  }
  input[type='checkbox']:disabled ~ .thumb {
    @apply border-gray-500 bg-gray-100;
  }
  input[type='checkbox']:focus + .track,
  input[type='checkbox']:active + .track {
    @apply outline outline-2;
  }
</style>
