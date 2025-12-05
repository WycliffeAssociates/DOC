import { writable } from 'svelte/store'
import type { Writable } from 'svelte/store'
export let langCodeAndNameStore: Writable<string> = writable('')
export let langCountStore: Writable<number> = writable<number>(0)

export let langCodesStore: Writable<Array<string>> = writable([])
export let langNamesStore: Writable<Array<string>> = writable([])
export let gatewayCodeAndNamesStore: Writable<Array<string>> = writable([])
export let heartCodeAndNamesStore: Writable<Array<string>> = writable([])
export let languagesClickedOrderStore: Writable<Array<string>> = writable([])
