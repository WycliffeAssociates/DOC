import { writable, Writable } from 'svelte/store'

let groupingOrderDefault: string = <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER
let chunkSizeDefault: string = <string>import.meta.env.VITE_CHUNK_SIZE_CHAPTER

export let layoutForPrintStore: Writable<boolean> = writable<boolean>(false)
export let limitTwStore: Writable<boolean> = writable<boolean>(true)
export let assemblyStrategyKindStore: Writable<string> =
  writable<string>(groupingOrderDefault)
export let assemblyStrategyChunkSizeStore: Writable<string> =
  writable<string>(chunkSizeDefault)
export let docTypeStore: Writable<string> = writable<string>('pdf')
export let generatePdfStore: Writable<boolean> = writable<boolean>(true)
export let generateEpubStore: Writable<boolean> = writable<boolean>(false)
export let generateDocxStore: Writable<boolean> = writable<boolean>(false)
export let emailStore: Writable<string | null> = writable<string | null>(null)
export let documentRequestKeyStore: Writable<string> = writable<string>('')
export let settingsUpdated: Writable<boolean> = writable<boolean>(false)
