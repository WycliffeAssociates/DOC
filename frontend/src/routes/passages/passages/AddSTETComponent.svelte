<script lang="ts">
  import { addBibleReference, removeBibleReference } from '$lib/passages/stores/PassagesStore'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguageStore'
  import { PUBLIC_STET_PASSAGES_URL } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import type { BibleReference } from './model'

  export let loading: boolean
  export let checkIcon: string
  let stetSuccessMessage: string = ''
  let isLoadingStetPassages = false

  async function getSTETPassages(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    stetPassagesUrl = <string>PUBLIC_STET_PASSAGES_URL
  ): Promise<Array<BibleReference>> {
    const url = `${apiRootUrl}${stetPassagesUrl}/${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bibleReferences: Array<BibleReference> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bibleReferences
  }

  export async function addSTETPassages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getSTETPassages(langCode)
      for (const bibleRef of bibleReferences) {
        addBibleReference(
          langCode,
          bibleRef.book_code,
          bibleRef.book_name,
          Number(bibleRef.start_chapter),
          bibleRef.start_chapter_verse_ref,
          Number(bibleRef.end_chapter),
          bibleRef.end_chapter_verse_ref
        )
      }
    } catch (error) {
      console.error('Failed to add STET passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }

  export async function removeSTETPassages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getSTETPassages(langCode)
      for (const bibleRef of bibleReferences) {
        removeBibleReference(
          langCode,
          bibleRef.book_code,
          Number(bibleRef.start_chapter),
          bibleRef.start_chapter_verse_ref,
          Number(bibleRef.end_chapter),
          bibleRef.end_chapter_verse_ref
        )
      }
    } catch (error) {
      console.error('Failed to remove STET passages:', error)
    } finally {
      console.log('STET passages removed successfully')
    }
  }

  async function handleAddSTETPassagesClick() {
    loading = true
    isLoadingStetPassages = true
    try {
      await addSTETPassages()
      stetSuccessMessage = '✔'
    } catch (error) {
      console.error('Error:', error)
    } finally {
      loading = false
      isLoadingStetPassages = false
    }
  }

  async function handleRemoveSTETPassagesClick() {
    loading = true
    isLoadingStetPassages = true
    try {
      await removeSTETPassages()
      stetSuccessMessage = ''
    } catch (error) {
      console.error('Error:', error)
    } finally {
      loading = false
      isLoadingStetPassages = false
    }
  }

  function handleSTETCheckboxClick(event: Event) {
    const target = event.target as HTMLInputElement
    if (target.checked) {
      handleAddSTETPassagesClick()
    } else {
      handleRemoveSTETPassagesClick()
    }
  }
</script>

<div id="stet-passages" class="mb-2 flex h-[56px] items-center">
  <input
    id="add-stet-passages-checkbox"
    type="checkbox"
    class="checkbox-target checkbox-style"
    on:click={handleSTETCheckboxClick}
  />
  <label
    for="add-stet-passages-checkbox"
    class="pl-1 text-xl text-[#33445C] {isLoadingStetPassages || stetSuccessMessage
      ? 'text-gray-400'
      : ''}">Add STET Passages</label
  >
  <div class="loader-container">
    {#if isLoadingStetPassages}
      <div class="loader"></div>
    {:else if stetSuccessMessage}
      <div class="success-message ml-2 text-green-500">
        {@html checkIcon}
      </div>
    {/if}
  </div>
</div>

<style>
  .success-message {
    transition: opacity 1s ease;
    opacity: 1;
  }
  .loader-container {
    display: flex;
    align-items: center;
  }
  .loader {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-top: 4px solid #4caf50;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
    margin-left: 8px;
  }
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
