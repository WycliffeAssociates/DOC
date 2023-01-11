import { writable, Writable } from 'svelte/store'

let groupingOrderDefault: string = <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER

export let layoutForPrintStore: Writable<boolean> = writable<boolean>(true)
export let assemblyStrategyKindStore: Writable<string> =
  writable<string>(groupingOrderDefault)
export let generatePdfStore: Writable<boolean> = writable<boolean>(false)
export let generateEpubStore: Writable<boolean> = writable<boolean>(false)
export let generateDocxStore: Writable<boolean> = writable<boolean>(false)
export let emailStore: Writable<string | null> = writable<string | null>(null)
export let documentRequestKeyStore: Writable<string> = writable<string>('')
