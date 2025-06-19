<script lang="ts">
  import { goto } from '$app/navigation'
  import LeftArrowIcon from '$lib/LeftArrowIcon.svelte'

  export let url = ''
</script>

<button
  class="flex items-center bg-white border border-[#E5E8EB]
               text-[#33445c] text-xl hover:bg-[#efefef] py-2 px-4 rounded-md"
  on:click={() => goto(url)}
>
  <LeftArrowIcon />
  <span class="hidden sm:inline">Back</span>
</button>
