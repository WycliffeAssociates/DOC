<script lang="ts">
  import { onMount } from 'svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import {
    addBibleReference,
    addAvailableBibleReference,
    removeBibleReference
  } from '$lib/passages/stores/PassagesStore'
  import { langCodesStore, langCountStore } from '$lib/passages/stores/LanguagesStore'
  import { PUBLIC_NT_SURVEY_RG_PASSAGES_URL } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import type { BibleReference } from './model'

  let loading: boolean = false
  export let checkIcon: string
  export let bookCodesAndNamesLang0: [string, string][]
  export let bookCodesAndNamesLang1: [string, string][]
  let ntSurveySuccessMessage: string = ''
  let isLoadingNTSurvey = false
  let lang0NtBibleReferences: Array<BibleReference> = []
  let lang1NtBibleReferences: Array<BibleReference> = []
  let availableLang0NtBibleReferences: Array<BibleReference> = []
  let availableLang1NtBibleReferences: Array<BibleReference> = []
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
    try {
      lang0NtBibleReferences = await getNTSurveyRGPassages($langCodesStore[0])
      // Filter down to the passages available in this language
      availableLang0NtBibleReferences = lang0NtBibleReferences.filter((ref) =>
        bookCodesAndNamesLang0.some(([code]) => code === ref.book_code)
      )
      if ($langCountStore > 1) {
        lang1NtBibleReferences = await getNTSurveyRGPassages($langCodesStore[1])
        // Filter down to the passages available in this language
        availableLang1NtBibleReferences = lang1NtBibleReferences.filter((ref) =>
          bookCodesAndNamesLang1.some(([code]) => code === ref.book_code)
        )
      }
      // Add availableLang0NtBibleReferences to filteredPassagesStore for
      // later reference in PassagesBasket
      for (const bibleRef of availableLang0NtBibleReferences) {
        addAvailableBibleReference(
          $langCodesStore[0],
          bibleRef.book_code,
          bibleRef.book_name,
          Number(bibleRef.start_chapter),
          bibleRef.start_chapter_verse_ref,
          Number(bibleRef.end_chapter),
          bibleRef.end_chapter_verse_ref
        )
      }
      // Add availableLang1NtBibleReferences to filteredPassagesStore for
      // later reference in PassagesBasket
      for (const bibleRef of availableLang1NtBibleReferences) {
        addAvailableBibleReference(
          $langCodesStore[1],
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
      showNT =
        availableLang0NtBibleReferences.length > 0 || availableLang1NtBibleReferences.length > 0
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
      // Add lang0 NT RG passages to the passageStore for reference in
      // PassagesBasket.svelte
      for (const bibleRef of lang0NtBibleReferences) {
        addBibleReference(
          $langCodesStore[0],
          bibleRef.book_code,
          bibleRef.book_name,
          Number(bibleRef.start_chapter),
          bibleRef.start_chapter_verse_ref,
          Number(bibleRef.end_chapter),
          bibleRef.end_chapter_verse_ref
        )
      }
      for (const bibleRef of lang1NtBibleReferences) {
        addBibleReference(
          $langCodesStore[1],
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
      // Remove the lang0 NT RG passages from the passageStore
      for (const bibleRef of lang0NtBibleReferences) {
        removeBibleReference(
          $langCodesStore[0],
          bibleRef.book_code,
          Number(bibleRef.start_chapter),
          bibleRef.start_chapter_verse_ref,
          Number(bibleRef.end_chapter),
          bibleRef.end_chapter_verse_ref
        )
      }
      // Remove the lang1 NT RG passages from the passageStore
      for (const bibleRef of lang1NtBibleReferences) {
        removeBibleReference(
          $langCodesStore[1],
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
  $: console.log('lang0NtBibleReferences:', lang0NtBibleReferences)
  $: console.log('lang1NtBibleReferences:', lang1NtBibleReferences)
  $: console.log('availableLang0NtBibleReferences:', availableLang0NtBibleReferences)
  $: console.log('availableLang1NtBibleReferences:', availableLang1NtBibleReferences)
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
