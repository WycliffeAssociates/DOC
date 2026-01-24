<script lang="ts">
  import { onMount } from 'svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import {
    addBibleReference,
    addFilteredBibleReference,
    removeBibleReference
  } from '$lib/passages/stores/PassagesStore'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguagesStore'
  import { PUBLIC_NT_SURVEY_RG_PASSAGES_URL } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import type { BibleReference } from './model'

  let loading: boolean = false
  export let checkIcon: string
  export let bookCodesAndNames: [string, string][]
  let ntSurveySuccessMessage: string = ''
  let isLoadingNTSurvey = false
  let ntBibleReferences: Array<BibleReference> = []
  let availableNtBibleReferences: Array<BibleReference> = []
  let showNT: boolean = false

  async function handleAddNTSurveyRGPassagesClick() {
    isLoadingNTSurvey = true
    try {
      await addNTSurveyRGPassages()
      ntSurveySuccessMessage = '✔'
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingNTSurvey = false
    }
  }

  async function handleRemoveNTSurveyRGPassagesClick() {
    isLoadingNTSurvey = true
    try {
      await removeNTSurveyRGPassages()
      ntSurveySuccessMessage = ''
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingNTSurvey = false
    }
  }

  function handleNTSurveyCheckboxClick(event: Event) {
    const target = event.target as HTMLInputElement
    if (target.checked) {
      handleAddNTSurveyRGPassagesClick()
    } else {
      handleRemoveNTSurveyRGPassagesClick()
    }
  }

  async function getNTSurveyRGPassages(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    ntSurveyRgPassagesUrl = <string>PUBLIC_NT_SURVEY_RG_PASSAGES_URL
  ): Promise<Array<BibleReference>> {
    const url = `${apiRootUrl}${ntSurveyRgPassagesUrl}/${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bibleReferences: Array<BibleReference> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bibleReferences
  }

  onMount(async () => {
    loading = true
    const langCode = $langCodeAndNameStore.split(',')[0]
    try {
      // Get all the NT RG passages
      ntBibleReferences = await getNTSurveyRGPassages(langCode)
      // Filter down to the passages available in this language
      availableNtBibleReferences = ntBibleReferences.filter((ref) =>
        bookCodesAndNames.some(([code]) => code === ref.book_code)
      )
      // Add availableNtBibleReferences to filteredPassagesStore for
      // later reference in PassagesBasket
      for (const bibleRef of availableNtBibleReferences) {
        addFilteredBibleReference(
          langCode,
          bibleRef.book_code,
          bibleRef.book_name,
          Number(bibleRef.start_chapter),
          bibleRef.start_chapter_verse_ref,
          Number(bibleRef.end_chapter),
          bibleRef.end_chapter_verse_ref
        )
      }
      // Set flag indicating if this language provides any of the NT
      // RG survey passages. We use this to show or not show the NT RG
      // passages checkbox
      showNT = availableNtBibleReferences.length > 0
      loading = false
    } catch (error) {
      console.error('Failed to load NT Survey RG passages:', error)
    } finally {
      console.log('NT Survey RG passages loaded successfully')
    }
    loading = false
  })

  export async function addNTSurveyRGPassages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      // Add all NT RG passages to the passageStore for reference in
      // PassagesBasket.svelte
      for (const bibleRef of ntBibleReferences) {
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
      console.error('Failed to add NT Survey RG passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }

  export async function removeNTSurveyRGPassages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      // Remove all the NT RG passages from the passageStore
      for (const bibleRef of ntBibleReferences) {
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
      console.error('Failed to remove NT Survey RG passages:', error)
    } finally {
      console.log('NT Survey RG Passages removed successfully')
    }
  }
  $: console.log(`ntBibleReferences: ${ntBibleReferences}`)
  $: console.log(`availableNtBibleReferences: ${availableNtBibleReferences}`)
</script>

{#if loading}
  <ProgressIndicator />
{/if}
{#if showNT}
  <div class="mb-4 flex items-center">
    <input
      id="add-nt-survey-passages-checkbox"
      type="checkbox"
      class="checkbox-target checkbox-style"
      on:click={handleNTSurveyCheckboxClick}
    />
    <label
      for="add-nt-survey-passages-checkbox"
      class="pl-1 text-xl font-bold text-[#33445C] {isLoadingNTSurvey || ntSurveySuccessMessage
        ? 'text-gray-400'
        : ''}">Add NT Survey Reviewers' Guide (RG) Passages</label
    >
    <div class="loader-container">
      {#if isLoadingNTSurvey}
        <div class="loader"></div>
      {:else if ntSurveySuccessMessage}
        <div class="success-message ml-2 text-green-500">
          {@html checkIcon}
        </div>
      {/if}
    </div>
  </div>
{/if}

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
