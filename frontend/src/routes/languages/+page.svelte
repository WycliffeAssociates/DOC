<script lang="ts">
  import { PUBLIC_LANGUAGE_BOOK_ORDER } from '$env/static/public'
  import {
    langCodesStore,
    langCountStore,
    langNamesStore,
    languagesClickedOrderStore
  } from '$lib/stores/LanguagesStore'
  import { ntBookStore, otBookStore, bookCountStore } from '$lib/stores/BooksStore'
  import { getResourceTypeLangCode } from '$lib/utils'
  import { resourceTypesStore, resourceTypesCountStore } from '$lib/stores/ResourceTypesStore'
  import { assemblyStrategyKindStore } from '$lib/stores/SettingsStore'
  import Languages from '$lib/Languages.svelte'
  import WizardBreadcrumb from '$lib/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/WizardBasket.svelte'
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'

  function handleLangChange(e: Event, lang: string) {
    const input = e.currentTarget as HTMLInputElement
    languagesClickedOrderStore.update((arr) => {
      if (input.checked) {
        // append only if not already present
        return arr.includes(lang) ? arr : [...arr, lang]
      } else {
        // remove if unchecked
        return arr.filter((v) => v !== lang)
      }
    })
  }

  $: {
    $resourceTypesStore = $resourceTypesStore.filter((item) =>
      $langCodesStore.includes(getResourceTypeLangCode(item))
    )
    $resourceTypesCountStore = $resourceTypesStore.length
  }

  $: {
    if ($langCountStore === 0) {
      $langCodesStore = []
      $langNamesStore = []
      $resourceTypesStore = []
      $resourceTypesCountStore = 0
      $otBookStore = []
      $ntBookStore = []
      $bookCountStore = 0
      $assemblyStrategyKindStore = <string>PUBLIC_LANGUAGE_BOOK_ORDER
    }
  }
</script>

<Languages
  message="Select up to 2 languages"
  {handleLangChange}
  {WizardBreadcrumb}
  {WizardBasket}
  {MobileLanguageDisplay}
  {DesktopLanguageDisplay}
  {languagesClickedOrderStore}
  {langCodesStore}
  {langNamesStore}
  {langCountStore}
/>
