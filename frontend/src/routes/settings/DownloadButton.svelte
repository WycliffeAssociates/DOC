<script lang="ts">
  function downloadFromUrl(url: string) {
    console.log(`url: ${url}`)
    window.open(url, '_blank')
  }
  export let url: string
  export let buttonText: string = 'View PDF'
  export let linkText: string = 'Download PDF'
  export let buttonClass: string = 'text-center p-4 blue-gradient w-1/2 rounded-md text-white'
</script>

<button class={buttonClass} on:click={() => downloadFromUrl(url)}>{buttonText}</button>
<!-- Right-click download link -->
<a href={url} class="mt-2 block text-sm text-blue-600 underline">
  {linkText}
  <span class="text-gray-500">(right-click → Save link as…)</span>
</a>

<style global lang="postcss">
  * :global(.orange-gradient) {
    background:
      linear-gradient(180deg, #fdd231 0%, #fdad29 100%),
      linear-gradient(0deg, rgba(20, 14, 8, 0.6), rgba(20, 14, 8, 0.6));
  }
  * :global(.blue-gradient) {
    background:
      linear-gradient(180deg, #1876fd 0%, #015ad9 100%), linear-gradient(0deg, #33445c, #33445c);
  }
</style>
