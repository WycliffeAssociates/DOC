import { browser } from '$app/environment'
import { goto } from '$app/navigation'
import {
  gatewayCodeAndNamesStore,
  heartCodeAndNamesStore,
  langCodeAndNameStore
} from '$lib/passages/stores/LanguagesStore'
import { documentReadyStore, errorStore } from '$lib/passages/stores/NotificationStore'
import { documentRequestKeyStore } from '$lib/passages/stores/SettingsStore'
import type { PassagesDocumentRequest } from '$lib/passages/models'

type StoreGroup = 'language' | 'settings' | 'notifications'

export let langRegExp = new RegExp('.*language.*')
export let passagesRegExp = new RegExp('.*passages/passages.*')
export let settingsRegExp = new RegExp('.*settings.*')

export function resetStores(storeGroup: StoreGroup) {
  if (storeGroup === 'language') {
    gatewayCodeAndNamesStore.set([])
    heartCodeAndNamesStore.set([])
    langCodeAndNameStore.set('')
  }

  if (storeGroup === 'settings') {
    documentRequestKeyStore.set('')
  }

  if (storeGroup === 'notifications') {
    documentReadyStore.set(false)
    errorStore.set(null)
  }
}

export function getName(codeAndName: string): string {
  return codeAndName?.split(/, (.*)/s)[1]
}
export function getCode(codeAndName: string): string {
  return codeAndName?.split(/, (.*)/s)[0]
}

export function routeToPage(url: string): void {
  if (browser) {
    goto(url)
  }
}

// Function to omit the 'id' from passageReferences just before stringifying
export function omitIdFromPassageReferences(documentRequest: PassagesDocumentRequest) {
  return {
    ...documentRequest,
    bibleReferences: documentRequest.bibleReferences.map(({ id, ...rest }) => rest) // Omit 'id'
  }
}
