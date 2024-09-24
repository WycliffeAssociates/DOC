<script lang="ts">
  import { goto } from '$app/navigation'
  import { page, navigating } from '$app/stores'
  import { langCodesStore } from '$lib/stet/stores/LanguagesStore'
  // import { bookCountStore } from '$lib/stores/BooksStore'
  // import { resourceTypesStore, resourceTypesCountStore } from '$lib/stores/ResourceTypesStore'
  import {
    // getResourceTypeLangCode,
    resetStores,
    sourceLangRegExp,
    targetLangRegExp,
    settingsRegExp
  } from '$lib/stet/utils'
  import { resetValuesStore } from '$lib/stet/stores/NotificationStore'
  import MobileBreadcrumb from '$lib/stet/MobileBreadcrumb.svelte'
  import DesktopBreadcrumb from '$lib/stet/DesktopBreadcrumb.svelte'

  function submitSourceLanguage() {
    resetStores('notifications')
    goto(`/stet/target_languages/${$langCodesStore[0]}`)
  }

  function submitTargetLanguage() {
    resetStores('notifications')
    goto('/stet/settings')
  }

  // Turn off and on breadcrumb number circles
  let turnSourceLangStepOn: boolean = false
  let turnTargetLangStepOn: boolean = false
  let turnSettingsStepOn: boolean = false
  // Title and label for breadcrumb for mobile (mobile = anything
  // under sm size according to our use of tailwindcss)
  let title: string = 'Source Language'
  let stepLabel: string = '1 of 3'
  $: {
    if (sourceLangRegExp.test($page.url.pathname)) {
      turnSourceLangStepOn = true
      title = 'Source Language'
      stepLabel = '1 of 3'
    } else if (targetLangRegExp.test($page.url.pathname)) {
      turnSourceLangStepOn = true
      turnTargetLangStepOn = true
      turnSettingsStepOn = false
      title = 'Target Language'
      stepLabel = '2 of 3'
    } else if (settingsRegExp.test($page.url.pathname)) {
      turnSourceLangStepOn = true
      turnTargetLangStepOn = true
      turnSettingsStepOn = true
      title = 'Review'
      stepLabel = '3 of 3'
    }
  }
</script>

<!-- wizard breadcrumb -->
<div class="border border-[#E5E8EB] p-4">
  <!-- if isMobile -->
  <MobileBreadcrumb
    {title}
    {stepLabel}
    {turnSourceLangStepOn}
    {turnTargetLangStepOn}
    {turnSettingsStepOn}
    {submitSourceLanguage}
    {submitTargetLanguage}
  />
  <!-- else -->
  <DesktopBreadcrumb
    {turnSourceLangStepOn}
    {turnTargetLangStepOn}
    {turnSettingsStepOn}
    {submitSourceLanguage}
    {submitTargetLanguage}
  />
  <!-- end if -->
</div>

<style lang="postcss">
  * :global(.next-button) {
    background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%),
      linear-gradient(0deg, #33445c, #33445c);
  }
  * :global(.next-button:hover) {
    background: linear-gradient(180deg, #0765ec 0%, #0149c8 100%),
      linear-gradient(0deg, #33445c, #33445c);
  }
</style>
