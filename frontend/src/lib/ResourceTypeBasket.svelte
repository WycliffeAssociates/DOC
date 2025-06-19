<script lang="ts">
  import { goto } from '$app/navigation'
  import { page, navigating } from '$app/stores'
  import { resourceTypeRegExp, getResourceTypeName, getResourceTypeLangCode } from '$lib/utils'
  import { bookCountStore } from '$lib/stores/BooksStore'
  import { resourceTypesStore, resourceTypesCountStore } from '$lib/stores/ResourceTypesStore'
  import FileIcon from './FileIcon.svelte'
  import EditIcon from './EditIcon.svelte'
  import CloseIcon from './CloseIcon.svelte'

  function uncheckResourceType(resourceTypeCodeAndName: string) {
    $resourceTypesStore = $resourceTypesStore.filter((item) => item != resourceTypeCodeAndName)
  }

  $: {
    if ($bookCountStore === 0) {
      $resourceTypesStore = []
      $resourceTypesCountStore = 0
    }
  }
</script>

{#if !resourceTypeRegExp.test($page.url.pathname) && $resourceTypesCountStore > 0}
  <div class="my-2 flex items-center justify-between">
    <div class="flex items-center justify-between">
      <FileIcon />
      <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Resource</h2>
    </div>
    <button
      class="flex rounded bg-white px-4 py-2 text-xl text-[#33445c] hover:bg-[#efefef]"
      on:click={() => goto('/resource_types')}
    >
      <EditIcon />
      <span class="ml-2"> Edit </span>
    </button>
  </div>
{:else}
  <div class="my-2 flex items-center">
    <FileIcon />
    <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Resource</h2>
  </div>
{/if}
{#if $resourceTypesCountStore > 0}
  {#each $resourceTypesStore as resourceTypeCodeAndName}
    {#if resourceTypeRegExp.test($page.url.pathname)}
      <div
        class="mt-2 inline-flex w-full items-center
                        justify-between rounded-lg bg-white p-4 text-xl
                        text-[#66768B]"
      >
        {getResourceTypeName(resourceTypeCodeAndName)} ({getResourceTypeLangCode(
          resourceTypeCodeAndName
        )})
        <button on:click={() => uncheckResourceType(resourceTypeCodeAndName)}>
          <CloseIcon />
        </button>
      </div>
    {:else}
      <div
        class="mt-2 inline-flex w-full items-center
                        justify-between rounded-lg bg-white p-4 text-xl
                        text-[#66768B]"
      >
        {getResourceTypeName(resourceTypeCodeAndName)} ({getResourceTypeLangCode(
          resourceTypeCodeAndName
        )})
      </div>
    {/if}
  {/each}
{:else}
  <div class="rounded-lg bg-[#e5e8eb] p-6 text-[#66768b]">
    Selections will appear here once a resource is selected
  </div>
{/if}
