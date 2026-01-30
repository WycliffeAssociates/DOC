<script lang="ts">
  import { onMount } from 'svelte'
  import { PUBLIC_CHAPTERS_IN_BOOKS_URL } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import AddPassageComponent from './AddPassageComponent.svelte'
  import AddOTComponent from './AddOTComponent.svelte'
  import AddNTComponent from './AddNTComponent.svelte'
  // import AddSTETComponent from './AddSTETComponent.svelte'

  let checkIcon =
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 0A8 8 0 1 0 8 16A8 8 0 0 0 8 0zM3.5 8.5l2.5 2.5L12.5 5l-1-1l-7 7l-2.5-2.5l-1 1z"/></svg>'

  export let chapters: Record<string, number[]> = {}
  export let bookCodesAndNamesLang0: [string, string][]
  export let bookCodesAndNamesLang1: [string, string][]

  async function getChaptersInBooks(
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    chaptersInBooksUrl = <string>PUBLIC_CHAPTERS_IN_BOOKS_URL
  ): Promise<Record<string, number[]>> {
    const response = await fetch(`${apiRootUrl}${chaptersInBooksUrl}`)
    const chaptersInBooks: Record<string, number[]> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return chaptersInBooks
  }

  onMount(async () => {
    try {
      chapters = await getChaptersInBooks()
    } catch (error) {
      console.error('Failed to get chapters:', error)
    } finally {
      console.log('Chapters retrieved successfully')
    }
  })
</script>

<div class="flex flex-col">
  <AddNTComponent {bookCodesAndNamesLang0} {bookCodesAndNamesLang1} {checkIcon} />
  <AddOTComponent {bookCodesAndNamesLang0} {bookCodesAndNamesLang1} {checkIcon} />
  <AddPassageComponent {chapters} {checkIcon} {bookCodesAndNamesLang0} {bookCodesAndNamesLang1} />
  <!-- <AddSTETComponent {bookCodesAndNames} {checkIcon} bind:loading /> -->
</div>
