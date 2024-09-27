<script lang="ts">
  import { getCode, getName } from '$lib/stet/utils'
  import {lang0CodeAndNameStore} from '$lib/stet/stores/LanguagesStore'

  export let showGatewayLanguages: boolean
  export let gatewayCodesAndNames: Array<string>
  export let heartCodesAndNames: Array<string>
  export let filteredGatewayCodeAndNames: Array<string>
  export let filteredHeartCodeAndNames: Array<string>
</script>

<main class="flex-1 overflow-y-auto p-4">
  {#if showGatewayLanguages}
    {#each gatewayCodesAndNames as langCodeAndName, index}
      <label for="lang-code-{index}">
        <div
          class="target py-2 pl-4"
          style={filteredGatewayCodeAndNames.includes(langCodeAndName) ? '' : 'display: none'}
        >
          <div class="target2 flex items-center justify-between">
            <div class="target3 flex items-center">
              <input
                id="lang-code-{index}"
                type="radio"
                bind:group={$lang0CodeAndNameStore}
                value={langCodeAndName}
                class="checkbox-target checkbox-style"
              />
              <span class="pl-1 text-xl text-[#33445C]">{getName(langCodeAndName)}</span>
            </div>
          </div>
          <div class="ml-6 text-xl text-[#33445C]">{getCode(langCodeAndName)}</div>
        </div>
      </label>
    {/each}
  {:else}
    {#each heartCodesAndNames as langCodeAndName, index}
      <label for="lang-code-{index}">
        <div
          class="target py-2 pl-4"
          style={filteredHeartCodeAndNames.includes(langCodeAndName) ? '' : 'display: none'}
        >
          <div class="target2 flex items-center justify-between">
            <div class="target3 flex items-center">
              <input
                id="lang-code-{index}"
                type="radio"
                bind:group={$lang0CodeAndNameStore}
                value={langCodeAndName}
                class="checkbox-target checkbox-style"
              />
              <span class="pl-1 text-xl text-[#33445C]">{getName(langCodeAndName)}</span>
            </div>
          </div>
          <div class="ml-6 text-xl text-[#33445C]">{getCode(langCodeAndName)}</div>
        </div>
      </label>
    {/each}
  {/if}
</main>
