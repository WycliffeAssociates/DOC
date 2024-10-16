import { writable } from 'svelte/store'
import type { Writable } from 'svelte/store'

export let resourceTypesStore: Writable<Array<string>> = writable<Array<string>>([])
export let lang0ResourceTypesStore: Writable<Array<string>> = writable<Array<string>>([])
export let lang1ResourceTypesStore: Writable<Array<string>> = writable<Array<string>>([])
export let resourceTypesCountStore: Writable<number> = writable<number>(0)
export let usfmAvailableStore: Writable<boolean> = writable<boolean>(false)
