<script lang="ts">
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'

  import Languages from '$lib/Languages.svelte'
  import WizardBreadcrumb from '$lib/passages/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/passages/WizardBasket.svelte'

  import {
    // langCodeAndNameStore,
    langCodesStore,
    langCountStore,
    langNamesStore,
    languagesClickedOrderStore
  } from '$lib/passages/stores/LanguagesStore'
</script>

<Languages
  message="Select up to 2 languages"
  {WizardBreadcrumb}
  {WizardBasket}
  {MobileLanguageDisplay}
  {DesktopLanguageDisplay}
  {languagesClickedOrderStore}
  {langCodesStore}
  {langNamesStore}
  {langCountStore}
/>
