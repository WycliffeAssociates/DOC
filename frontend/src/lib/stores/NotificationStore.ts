import { writable } from 'svelte/store'
import type { Writable } from 'svelte/store'

export let documentReadyStore: Writable<boolean> = writable(false)
export let errorStore: Writable<string | null | undefined> = writable(undefined)
export let resetValuesStore: Writable<boolean> = writable(false)
