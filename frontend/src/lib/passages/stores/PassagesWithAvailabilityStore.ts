import { derived } from 'svelte/store'
import { passagesStore, availablePassagesStore } from '$lib/passages/stores/PassagesStore'
import type { BibleReference } from '$lib/passages/models'
import { isAvailable } from '$lib/passages/utils'

export const passagesWithAvailabilityStore = derived(
  [passagesStore, availablePassagesStore],
  ([$passages, $available]) => {
    return $passages.map((p) => ({
      passage: p,
      available: $available ? isAvailable(p, $available) : false
    }))
  }
)
