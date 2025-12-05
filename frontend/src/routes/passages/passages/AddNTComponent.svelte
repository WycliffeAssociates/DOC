<script lang="ts">
  import { onMount } from 'svelte'
  import {
    addBibleReference,
    addFilteredBibleReference,
    removeBibleReference
  } from '$lib/passages/stores/PassagesStore'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguagesStore'
  import { PUBLIC_NT_SURVEY_RG_PASSAGES_URL } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import type { BibleReference } from './model'

  export let loading: boolean
  export let checkIcon: string
  export let bookCodesAndNames: [string, string][]
  let showNT: boolean = false
  let ntSurveySuccessMessage: string = ''
  let isLoadingNTSurvey = false

  async function handleAddNTSurveyRGPassagesClick() {
    loading = true
    isLoadingNTSurvey = true
    try {
      await addNTSurveyRGPassages()
      ntSurveySuccessMessage = '✔'
    } catch (error) {
      console.error('Error:', error)
    } finally {
      loading = false
      isLoadingNTSurvey = false
    }
  }

  async function handleRemoveNTSurveyRGPassagesClick() {
    loading = true
    isLoadingNTSurvey = true
    try {
      await removeNTSurveyRGPassages()
      ntSurveySuccessMessage = ''
    } catch (error) {
      console.error('Error:', error)
    } finally {
      loading = false
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
  ): Promise<[Array<BibleReference>, Array<BibleReference>]> {
    const url = `${apiRootUrl}${ntSurveyRgPassagesUrl}/${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bibleReferences: Array<BibleReference> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return [
      bibleReferences,
      bibleReferences.filter((ref) => bookCodesAndNames.some(([code]) => code === ref.book_code))
    ]
  }

  onMount(async () => {
    const langCode = $langCodeAndNameStore.split(',')[0]
    try {
      const [ntRgPassages, _] = await getNTSurveyRGPassages(langCode)
      showNT = ntRgPassages.length > 0
    } catch (error) {
      console.error('Failed to add NT Survey RG passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  })

  export async function addNTSurveyRGPassages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const [bibleReferences, bibleReferencesFiltered] = await getNTSurveyRGPassages(langCode)
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
      for (const bibleRef of bibleReferencesFiltered) {
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
    } catch (error) {
      console.error('Failed to add NT Survey RG passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }

  export async function removeNTSurveyRGPassages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const [bibleReferences, bibleReferencesFiltered] = await getNTSurveyRGPassages(langCode)
      console.log(`bibleReferences[0]: ${bibleReferences[0]}`)
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
      console.error('Failed to remove NT Survey RG passages:', error)
    } finally {
      console.log('NT Survey RG Passages removed successfully')
    }
  }
</script>

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
