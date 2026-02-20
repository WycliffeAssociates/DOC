<script lang="ts">
  import MobileLanguageDisplay from './MobileLanguageDisplay.svelte'
  import DesktopLanguageDisplay from './DesktopLanguageDisplay.svelte'

  import Languages from '$lib/Languages.svelte'
  import WizardBreadcrumb from '$lib/passages/WizardBreadcrumb.svelte'
  import WizardBasket from '$lib/passages/WizardBasket.svelte'
  import { passagesStore, availablePassagesStore } from '$lib/passages/stores/PassagesStore'
  import type { BibleReference } from '$lib/passages/models'

  import {
    langCodesStore,
    langCountStore,
    langNamesStore,
    languagesClickedOrderStore
  } from '$lib/passages/stores/LanguagesStore'

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
    // keep only passages whose langCode is still selected
    const allowedLangs = new Set(
      $languagesClickedOrderStore.map((s) => {
        const [langCode] = s.split(',')
        return langCode
      })
    )
    passagesStore.update((passages) =>
      passages.filter((p: BibleReference) => p.langCode !== null && allowedLangs.has(p.langCode))
    )
    availablePassagesStore.update((passages) =>
      passages.filter((p: BibleReference) => p.langCode !== null && allowedLangs.has(p.langCode))
    )
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
