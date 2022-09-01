<script lang="ts">
  import { push } from 'svelte-spa-router'
  import { ntBookStore, otBookStore } from '../stores/BooksStore'
  import {
    lang0CodeStore,
    lang1CodeStore,
    lang0NameStore,
    lang1NameStore,
    langCountStore
  } from '../stores/LanguagesStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore,
    resourceTypesCountStore
  } from '../stores/ResourceTypesStore'
  import LeftArrow from './LeftArrow.svelte'
  import ProgressIndicator from './ProgressIndicator.svelte'
  import { resetStores } from '../lib/utils'

  async function getResourceTypesAndNames(
    langCode: string,
    resourceCodeAndNames: Array<[string, string]>,
    apiRootUrl = <string>import.meta.env.VITE_BACKEND_API_URL,
    resourceTypesUrl = <string>import.meta.env.VITE_RESOURCE_TYPES_URL
  ): Promise<Array<[string, string]>> {
    const url_ = `${apiRootUrl}${resourceTypesUrl}${langCode}/`
    const url = new URL(url_)
    resourceCodeAndNames.map(resourceCodeAndName =>
      url.searchParams.append('resource_codes', resourceCodeAndName[0])
    )
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const resourceTypesAndNames: Array<[string, string]> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    // const codes = resourceTypesAndNames.map((x: [string, string]) => x[0])
    // console.log(`codes: ${codes}`)

    return resourceTypesAndNames
  }

  // Resolve promise for data
  let lang0ResourceTypesAndNames: Array<string>
  $: {
    if ($lang0CodeStore) {
      let otResourceCodes_: Array<[string, string]> = $otBookStore.map(item => [
        item.split(', ')[0],
        item.split(', ')[1]
      ])
      let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map(item => [
        item.split(', ')[0],
        item.split(', ')[1]
      ])
      getResourceTypesAndNames($lang0CodeStore, [
        ...otResourceCodes_,
        ...ntResourceCodes_
      ])
        .then(resourceTypesAndNames => {
          lang0ResourceTypesAndNames = resourceTypesAndNames.map(
            tuple => `${tuple[0]}, ${tuple[1]}`
          )
        })
        .catch(err => console.error(err))
    }
  }

  // Resolve promise for data for language
  let lang1ResourceTypesAndNames: Array<string>
  $: {
    if ($lang1CodeStore) {
      let otResourceCodes_: Array<[string, string]> = $otBookStore.map(item => [
        item.split(', ')[0],
        item.split(', ')[1]
      ])
      let ntResourceCodes_: Array<[string, string]> = $ntBookStore.map(item => [
        item.split(', ')[0],
        item.split(', ')[1]
      ])
      getResourceTypesAndNames($lang1CodeStore, [
        ...otResourceCodes_,
        ...ntResourceCodes_
      ])
        .then(resourceTypesAndNames => {
          lang1ResourceTypesAndNames = resourceTypesAndNames.map(
            tuple => `${tuple[0]}, ${tuple[1]}`
          )
        })
        .catch(err => console.error(err))
    }
  }

  function selectAllLang0ResourceTypes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      lang0ResourceTypesStore.set(lang0ResourceTypesAndNames)
    } else {
      lang0ResourceTypesStore.set([])
    }
  }

  function selectAllLang1ResourceTypes(event: Event) {
    if ((<HTMLInputElement>event.target).checked) {
      lang1ResourceTypesStore.set(lang1ResourceTypesAndNames)
    } else {
      lang1ResourceTypesStore.set([])
    }
  }

  function resetResourceTypes() {
    resetStores('resource_types')
  }

  function submitResourceTypes() {
    push('#/')
  }

  // Keep track of how many resources are currently stored reactively.
  let nonEmptyLang0Resourcetypes: boolean
  $: nonEmptyLang0Resourcetypes = $lang0ResourceTypesStore.every(item => item.length > 0)

  let nonEmptyLang1Resourcetypes: boolean
  $: nonEmptyLang1Resourcetypes = $lang1ResourceTypesStore.every(item => item.length > 0)

  $: {
    if (nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set(
        $lang0ResourceTypesStore.length + $lang1ResourceTypesStore.length
      )
    } else if (nonEmptyLang0Resourcetypes && !nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set($lang0ResourceTypesStore.length)
    } else if (!nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCountStore.set($lang1ResourceTypesStore.length)
    } else {
      resourceTypesCountStore.set(0)
    }
  }
</script>

<div class="bg-white flex">
  <button
    class="bg-white hover:bg-grey-100 text-grey-darkest font-bold py-2 px-4 rounded inline-flex items-center"
    on:click={() => push('#/')}
  >
    <LeftArrow backLabel="Resource Types" />
  </button>
</div>
<div class="bg-white pl-4">
  <div class="grid grid-cols-2 gap-4 bg-white">
    {#if $langCountStore > 0}
      <div>
        {#if !lang0ResourceTypesAndNames}
          <ProgressIndicator />
        {:else}
          <div>
            <div>
              <h3 class="text-primary-content mb-4">
                Resource types available for
                {$lang0NameStore}
              </h3>
              {#if lang0ResourceTypesAndNames.length > 0}
                <div>
                  <label
                    for="select-all-lang0-resource-types"
                    class="text-primary-content"
                    >Select all {$lang0NameStore}'s resource types</label
                  >
                  <input
                    id="select-all-lang0-resource-types"
                    type="checkbox"
                    class="checkbox"
                    on:change={event => selectAllLang0ResourceTypes(event)}
                  />
                </div>
              {/if}
              <ul class="pb-4">
                {#each lang0ResourceTypesAndNames as resourceTypeAndName, index}
                  <li>
                    <label for="lang0-resourcetype-{index}" class="text-primary-content"
                      >{resourceTypeAndName.split(', ')[1]}</label
                    >
                    <input
                      id="lang0-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$lang0ResourceTypesStore}
                      value={resourceTypeAndName}
                      class="checkbox"
                    />
                  </li>
                {/each}
              </ul>
            </div>
          </div>
        {/if}
      </div>
    {/if}
    {#if $langCountStore > 1}
      <div>
        {#if !lang1ResourceTypesAndNames}
          <ProgressIndicator />
        {:else}
          <div>
            <div>
              <h3 class="text-primary-content mb-4">
                Resource types available for {$lang1NameStore}
              </h3>
              {#if lang1ResourceTypesAndNames.length > 0}
                <div>
                  <label
                    for="select-all-lang1-resource-types"
                    class="text-primary-content"
                    >Select all
                    {$lang1NameStore}'s resource types</label
                  >
                  <input
                    id="select-all-lang1-resource-types"
                    type="checkbox"
                    class="checkbox"
                    on:change={event => selectAllLang1ResourceTypes(event)}
                  />
                </div>
              {/if}
              <ul>
                {#each lang1ResourceTypesAndNames as resourceTypeAndName, index}
                  <li>
                    <label for="lang1-resourcetype-{index}" class="text-primary-content"
                      >{resourceTypeAndName.split(', ')[1]}</label
                    >
                    <input
                      id="lang1-resourcetype-{index}"
                      type="checkbox"
                      bind:group={$lang1ResourceTypesStore}
                      value={resourceTypeAndName}
                      class="checkbox"
                    />
                  </li>
                {/each}
              </ul>
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  {#if $resourceTypesCountStore > 0}
    <div class="text-center px-2 pt-2 mb-8 mt-2">
      <button
        on:click|preventDefault={submitResourceTypes}
        class="btn w-5/6 orange-gradient text-primary-content capitalize"
        >Add ({$resourceTypesCountStore}) Resource Types</button
      >
    </div>

    <!-- <div class="mx-auto w-full px-2 pt-2 mt-2"> -->
    <!--   <button on:click|preventDefault={resetResourceTypes} class="btn reset-button" -->
    <!--     >Reset resource types</button -->
    <!--   > -->
    <!-- </div> -->
  {/if}
</div>

<style global lang="postcss">
  * :global(.reset-button) {
    background-color: red;
  }

  * :global(.orange-gradient) {
    background: linear-gradient(180deg, #fdd231 0%, #fdad29 100%),
      linear-gradient(0deg, rgba(20, 14, 8, 0.6), rgba(20, 14, 8, 0.6));
  }
</style>