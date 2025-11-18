import { writable } from 'svelte/store'
import type { Writable } from 'svelte/store'
export let docTypeStore: Writable<string> = writable<string>('docx')
export let emailStore: Writable<string | null> = writable<string | null>(null)
export let documentRequestKeyStore: Writable<string> = writable<string>('')
export let settingsUpdatedStore: Writable<boolean> = writable<boolean>(false)
