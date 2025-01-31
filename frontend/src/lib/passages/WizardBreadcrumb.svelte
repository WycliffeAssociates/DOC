<script lang="ts">
  import { goto } from '$app/navigation'
  import { page, navigating } from '$app/stores'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguageStore'
  import { resetStores, langRegExp, passagesRegExp, settingsRegExp } from '$lib/passages/utils'
  import MobileBreadcrumb from '$lib/passages/MobileBreadcrumb.svelte'
  import DesktopBreadcrumb from '$lib/passages/DesktopBreadcrumb.svelte'

  function submitLanguage() {
    resetStores('notifications')
    goto(`/passages/passages`)
  }

  function submitPassages() {
    resetStores('notifications')
    goto('/passages/settings')
  }

  // Turn off and on breadcrumb number circles
  let turnLangStepOn: boolean = false
  let turnPassagesStepOn: boolean = false
  let turnSettingsStepOn: boolean = false
  // Title and label for breadcrumb for mobile (mobile = anything
  // under sm size according to our use of tailwindcss)
  let title: string = 'Language'
  let stepLabel: string = '1 of 3'
  $: {
    if (langRegExp.test($page.url.pathname)) {
      turnLangStepOn = true
      title = 'Language'
      stepLabel = '1 of 3'
    } else if (passagesRegExp.test($page.url.pathname)) {
      turnLangStepOn = true
      turnPassagesStepOn = true
      turnSettingsStepOn = false
      title = 'Passages'
      stepLabel = '2 of 3'
    } else if (settingsRegExp.test($page.url.pathname)) {
      turnLangStepOn = true
      turnPassagesStepOn = true
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
    {turnLangStepOn}
    {turnPassagesStepOn}
    {turnSettingsStepOn}
    {submitLanguage}
    {submitPassages}
  />
  <!-- else -->
  <DesktopBreadcrumb
    {turnLangStepOn}
    {turnPassagesStepOn}
    {turnSettingsStepOn}
    {submitLanguage}
    {submitPassages}
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
