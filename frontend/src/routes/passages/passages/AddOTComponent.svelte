<script lang="ts">
  import { onMount } from 'svelte'
  import ProgressIndicator from '$lib/ProgressIndicator.svelte'
  import {
    PUBLIC_OT_SURVEY_RG1_PASSAGES_URL,
    PUBLIC_OT_SURVEY_RG2_PASSAGES_URL,
    PUBLIC_OT_SURVEY_RG3_PASSAGES_URL,
    PUBLIC_OT_SURVEY_RG4_PASSAGES_URL
  } from '$env/static/public'
  import { env } from '$env/dynamic/public'
  import type { BibleReference } from './model'
  import { langCodeAndNameStore } from '$lib/passages/stores/LanguagesStore'
  import {
    addBibleReference,
    addFilteredBibleReference,
    removeBibleReference
  } from '$lib/passages/stores/PassagesStore'
  import { bookRange } from '$lib/bible-books'
  import type { BookKey } from '$lib/bible-books'

  let loading: boolean = false
  export let checkIcon: string
  export let bookCodesAndNames: [string, string][]
  let isLoadingOTSurveyRG1 = false
  let isLoadingOTSurveyRG2 = false
  let isLoadingOTSurveyRG3 = false
  let isLoadingOTSurveyRG4 = false
  let otSurveyRG1SuccessMessage: string = ''
  let otSurveyRG2SuccessMessage: string = ''
  let otSurveyRG3SuccessMessage: string = ''
  let otSurveyRG4SuccessMessage: string = ''
  let rg1BibleReferences: Array<BibleReference> = []
  let availableRg1BibleReferences: Array<BibleReference> = []
  let showRG1: boolean = false
  let rg2BibleReferences: Array<BibleReference> = []
  let availableRg2BibleReferences: Array<BibleReference> = []
  let showRG2: boolean = false
  let rg3BibleReferences: Array<BibleReference> = []
  let availableRg3BibleReferences: Array<BibleReference> = []
  let showRG3: boolean = false
  let rg4BibleReferences: Array<BibleReference> = []
  let availableRg4BibleReferences: Array<BibleReference> = []
  let showRG4: boolean = false

  async function getOTSurveyRG1Passages(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    otSurveyRg1PassagesUrl = <string>PUBLIC_OT_SURVEY_RG1_PASSAGES_URL
  ): Promise<Array<BibleReference>> {
    const url = `${apiRootUrl}${otSurveyRg1PassagesUrl}/${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bibleReferences: Array<BibleReference> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bibleReferences
  }

  async function getOTSurveyRG2Passages(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    otSurveyRg2PassagesUrl = <string>PUBLIC_OT_SURVEY_RG2_PASSAGES_URL
  ): Promise<Array<BibleReference>> {
    const url = `${apiRootUrl}${otSurveyRg2PassagesUrl}/${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bibleReferences: Array<BibleReference> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bibleReferences
  }

  async function getOTSurveyRG3Passages(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    otSurveyRg3PassagesUrl = <string>PUBLIC_OT_SURVEY_RG3_PASSAGES_URL
  ): Promise<Array<BibleReference>> {
    const url = `${apiRootUrl}${otSurveyRg3PassagesUrl}/${langCode}`
    console.log(`url: ${url}`)
    const response = await fetch(url)
    const bibleReferences: Array<BibleReference> = await response.json()
    if (!response.ok) {
      console.error(response.statusText)
      throw new Error(response.statusText)
    }
    return bibleReferences
  }

  async function getOTSurveyRG4Passages(
    langCode: string,
    apiRootUrl = env.PUBLIC_BACKEND_API_URL,
    otSurveyRg4PassagesUrl = <string>PUBLIC_OT_SURVEY_RG4_PASSAGES_URL
  ): Promise<Array<BibleReference>> {
    const url = `${apiRootUrl}${otSurveyRg4PassagesUrl}/${langCode}`
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
      // Get all the OT RG 1 passages
      rg1BibleReferences = await getOTSurveyRG1Passages(langCode)
      // Filter down to the OT RG 1 passages available in this language
      availableRg1BibleReferences = rg1BibleReferences.filter((ref) =>
        bookCodesAndNames.some(([code]) => code === ref.book_code)
      )
      // Add available bible references to filteredPassagesStore for
      // later reference in PassagesBasket
      for (const bibleRef of availableRg1BibleReferences) {
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
      // Set flag indicating if this language provides any of the OT
      // RG 1 survey passages.
      showRG1 = availableRg1BibleReferences.length > 0

      // Get all the OT RG 2 passages
      rg2BibleReferences = await getOTSurveyRG2Passages(langCode)
      // Filter down to the OT RG 2 passages available in this language
      availableRg2BibleReferences = rg2BibleReferences.filter((ref) =>
        bookCodesAndNames.some(([code]) => code === ref.book_code)
      )
      // Add available bible references to filteredPassagesStore for
      // later reference in PassagesBasket
      for (const bibleRef of availableRg2BibleReferences) {
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
      // Set flag indicating if this language provides any of the 0T
      // RG 2 survey passages.
      showRG2 = availableRg2BibleReferences.length > 0

      // Get all the OT RG 3 passages
      rg3BibleReferences = await getOTSurveyRG3Passages(langCode)
      // Filter down to the OT RG 3 passages available in this language
      availableRg3BibleReferences = rg3BibleReferences.filter((ref) =>
        bookCodesAndNames.some(([code]) => code === ref.book_code)
      )
      // Add available bible references to filteredPassagesStore for
      // later reference in PassagesBasket
      for (const bibleRef of availableRg3BibleReferences) {
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
      // Set flag indicating if this language provides any of the 0T
      // RG 3 survey passages.
      showRG3 = availableRg3BibleReferences.length > 0

      // Get all the OT RG 4 passages
      rg4BibleReferences = await getOTSurveyRG4Passages(langCode)
      // Filter down to the OT RG 4 passages available in this language
      availableRg4BibleReferences = rg4BibleReferences.filter((ref) =>
        bookCodesAndNames.some(([code]) => code === ref.book_code)
      )
      // Add available bible references to filteredPassagesStore for
      // later reference in PassagesBasket
      for (const bibleRef of availableRg4BibleReferences) {
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
      // Set flag indicating if this language provides any of the 0T
      // RG 4 survey passages.
      showRG4 = availableRg4BibleReferences.length > 0
    } catch (error) {
      console.error('Failed to load NT Survey RG passages:', error)
    } finally {
      console.log('NT Survey RG passages loaded successfully')
    }
    loading = false
  })

  export async function addOTSurveyRG1Passages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getOTSurveyRG1Passages(langCode)
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
      console.error('Failed to add OT Survey RG1 passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }

  export async function addOTSurveyRG2Passages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getOTSurveyRG2Passages(langCode)
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
      console.error('Failed to add OT Survey RG2 passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }

  export async function addOTSurveyRG3Passages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getOTSurveyRG3Passages(langCode)
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
      console.error('Failed to add OT Survey RG3 passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }

  export async function addOTSurveyRG4Passages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getOTSurveyRG4Passages(langCode)
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
      console.error('Failed to add OT Survey RG4 passages:', error)
    } finally {
      console.log('Passages added successfully')
    }
  }

  export async function removeOTSurveyRG1Passages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getOTSurveyRG1Passages(langCode)
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
      console.error('Failed to remove OT Survey RG1 passages:', error)
    } finally {
      console.log('OT Survey RG1 Passages removed successfully')
    }
  }

  export async function removeOTSurveyRG2Passages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getOTSurveyRG2Passages(langCode)
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
      console.error('Failed to remove OT Survey RG2 passages:', error)
    } finally {
      console.log('OT Survey RG2 Passages removed successfully')
    }
  }

  export async function removeOTSurveyRG3Passages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getOTSurveyRG3Passages(langCode)
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
      console.error('Failed to remove OT Survey RG3 passages:', error)
    } finally {
      console.log('OT Survey RG3 Passages removed successfully')
    }
  }

  export async function removeOTSurveyRG4Passages() {
    try {
      const langCode = $langCodeAndNameStore.split(',')[0]
      const bibleReferences = await getOTSurveyRG4Passages(langCode)
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
      console.error('Failed to remove OT Survey RG4 passages:', error)
    } finally {
      console.log('OT Survey RG4 Passages removed successfully')
    }
  }

  async function handleAddOTSurveyRG1PassagesClick() {
    isLoadingOTSurveyRG1 = true
    try {
      await addOTSurveyRG1Passages()
      otSurveyRG1SuccessMessage = '✔'
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingOTSurveyRG1 = false
    }
  }

  async function handleAddOTSurveyRG2PassagesClick() {
    isLoadingOTSurveyRG2 = true
    try {
      await addOTSurveyRG2Passages()
      otSurveyRG2SuccessMessage = '✔'
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingOTSurveyRG2 = false
    }
  }

  async function handleAddOTSurveyRG3PassagesClick() {
    isLoadingOTSurveyRG3 = true
    try {
      await addOTSurveyRG3Passages()
      otSurveyRG3SuccessMessage = '✔'
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingOTSurveyRG3 = false
    }
  }

  async function handleAddOTSurveyRG4PassagesClick() {
    isLoadingOTSurveyRG4 = true
    try {
      await addOTSurveyRG4Passages()
      otSurveyRG4SuccessMessage = '✔'
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingOTSurveyRG4 = false
    }
  }

  async function handleRemoveOTSurveyRG1PassagesClick() {
    isLoadingOTSurveyRG1 = true
    try {
      await removeOTSurveyRG1Passages()
      otSurveyRG1SuccessMessage = ''
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingOTSurveyRG1 = false
    }
  }

  async function handleRemoveOTSurveyRG2PassagesClick() {
    isLoadingOTSurveyRG2 = true
    try {
      await removeOTSurveyRG2Passages()
      otSurveyRG2SuccessMessage = ''
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingOTSurveyRG2 = false
    }
  }

  async function handleRemoveOTSurveyRG3PassagesClick() {
    isLoadingOTSurveyRG3 = true
    try {
      await removeOTSurveyRG3Passages()
      otSurveyRG3SuccessMessage = ''
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingOTSurveyRG3 = false
    }
  }

  async function handleRemoveOTSurveyRG4PassagesClick() {
    isLoadingOTSurveyRG4 = true
    try {
      await removeOTSurveyRG4Passages()
      otSurveyRG4SuccessMessage = ''
    } catch (error) {
      console.error('Error:', error)
    } finally {
      isLoadingOTSurveyRG4 = false
    }
  }

  let otSurveyRG1Checked = false
  let otSurveyRG2Checked = false
  let otSurveyRG3Checked = false
  let otSurveyRG4Checked = false
  let allOTSurveyChecked = false

  function handleSelectAllClick(event: Event) {
    const target = event.target as HTMLInputElement
    allOTSurveyChecked = target.checked
    if (showRG1) {
      otSurveyRG1Checked = target.checked
    }
    if (showRG2) {
      otSurveyRG2Checked = target.checked
    }
    if (showRG3) {
      otSurveyRG3Checked = target.checked
    }
    if (showRG4) {
      otSurveyRG4Checked = target.checked
    }
    if (target.checked) {
      if (showRG1) {
        handleAddOTSurveyRG1PassagesClick()
      }
      if (showRG2) {
        handleAddOTSurveyRG2PassagesClick()
      }
      if (showRG3) {
        handleAddOTSurveyRG3PassagesClick()
      }
      if (showRG4) {
        handleAddOTSurveyRG4PassagesClick()
      }
    } else {
      handleRemoveOTSurveyRG1PassagesClick()
      handleRemoveOTSurveyRG2PassagesClick()
      handleRemoveOTSurveyRG3PassagesClick()
      handleRemoveOTSurveyRG4PassagesClick()
    }
  }

  function handleOTSurvey1CheckboxClick(event: Event) {
    const target = event.target as HTMLInputElement
    otSurveyRG1Checked = target.checked
    if (target.checked) {
      handleAddOTSurveyRG1PassagesClick()
    } else {
      handleRemoveOTSurveyRG1PassagesClick()
    }
    updateSelectAll()
  }

  function handleOTSurvey2CheckboxClick(event: Event) {
    const target = event.target as HTMLInputElement
    otSurveyRG2Checked = target.checked
    if (target.checked) {
      handleAddOTSurveyRG2PassagesClick()
    } else {
      handleRemoveOTSurveyRG2PassagesClick()
    }
    updateSelectAll()
  }

  function handleOTSurvey3CheckboxClick(event: Event) {
    const target = event.target as HTMLInputElement
    otSurveyRG3Checked = target.checked
    if (target.checked) {
      handleAddOTSurveyRG3PassagesClick()
    } else {
      handleRemoveOTSurveyRG3PassagesClick()
    }
    updateSelectAll()
  }

  function handleOTSurvey4CheckboxClick(event: Event) {
    const target = event.target as HTMLInputElement
    otSurveyRG4Checked = target.checked
    if (target.checked) {
      handleAddOTSurveyRG4PassagesClick()
    } else {
      handleRemoveOTSurveyRG4PassagesClick()
    }
    updateSelectAll()
  }

  function updateSelectAll() {
    allOTSurveyChecked =
      (showRG1 ? otSurveyRG1Checked : true) &&
      (showRG2 ? otSurveyRG2Checked : true) &&
      (showRG3 ? otSurveyRG3Checked : true) &&
      (showRG4 ? otSurveyRG4Checked : true)
  }
</script>

{#if loading}
  <ProgressIndicator />
{/if}
{#if [showRG1, showRG2, showRG3, showRG4].filter(Boolean).length > 1}
  <div class="mb-2 mt-4 flex items-center">
    <input
      id="add-all-ot-survey-passages-checkbox"
      type="checkbox"
      bind:checked={allOTSurveyChecked}
      class="checkbox-target checkbox-style"
      on:click={handleSelectAllClick}
    />
    <label for="add-all-ot-survey-passages-checkbox" class="pl-1 text-xl font-bold text-[#33445C]"
      >Add all OT Survey Reviewers' Guide (RG) Passages</label
    >
  </div>
{/if}
{#if showRG1}
  <div class="mb-2 flex items-center">
    <input
      id="add-ot-survey-passages-rg1-checkbox"
      type="checkbox"
      bind:checked={otSurveyRG1Checked}
      class="checkbox-target checkbox-style"
      on:click={handleOTSurvey1CheckboxClick}
    />
    <label
      for="add-ot-survey-passages-rg1-checkbox"
      class="pl-1 text-xl text-[#33445C] {isLoadingOTSurveyRG1 || otSurveyRG1SuccessMessage
        ? 'text-gray-400'
        : ''}">Add OT Survey RG1 Passages only (Genesis to Deuteronomy)</label
    >
    <div class="loader-container">
      {#if isLoadingOTSurveyRG1}
        <div class="loader"></div>
      {:else if otSurveyRG1SuccessMessage}
        <div class="success-message ml-2 text-green-500">
          {@html checkIcon}
        </div>
      {/if}
    </div>
  </div>
{/if}
{#if showRG2}
  <div class="mb-2 flex items-center">
    <input
      id="add-ot-survey-passages-rg2-checkbox"
      type="checkbox"
      bind:checked={otSurveyRG2Checked}
      class="checkbox-target checkbox-style"
      on:click={handleOTSurvey2CheckboxClick}
    />
    <label
      for="add-ot-survey-passages-rg2-checkbox"
      class="pl-1 text-xl text-[#33445C] {isLoadingOTSurveyRG2 || otSurveyRG2SuccessMessage
        ? 'text-gray-400'
        : ''}">Add OT Survey RG2 Passages only (Joshua to Esther)</label
    >
    <div class="loader-container">
      {#if isLoadingOTSurveyRG2}
        <div class="loader"></div>
      {:else if otSurveyRG2SuccessMessage}
        <div class="success-message ml-2 text-green-500">
          {@html checkIcon}
        </div>
      {/if}
    </div>
  </div>
{/if}
{#if showRG3}
  <div class="mb-2 flex items-center">
    <input
      id="add-ot-survey-passages-rg3-checkbox"
      type="checkbox"
      bind:checked={otSurveyRG3Checked}
      class="checkbox-target checkbox-style"
      on:click={handleOTSurvey3CheckboxClick}
    />
    <label
      for="add-ot-survey-passages-rg3-checkbox"
      class="pl-1 text-xl text-[#33445C] {isLoadingOTSurveyRG3 || otSurveyRG3SuccessMessage
        ? 'text-gray-400'
        : ''}">Add OT Survey RG3 Passages only (Job to Song of Songs)</label
    >
    <div class="loader-container">
      {#if isLoadingOTSurveyRG3}
        <div class="loader"></div>
      {:else if otSurveyRG3SuccessMessage}
        <div class="success-message ml-2 text-green-500">
          {@html checkIcon}
        </div>
      {/if}
    </div>
  </div>
{/if}
{#if showRG4}
  <div class="mb-2 flex items-center">
    <input
      id="add-ot-survey-passages-rg4-checkbox"
      type="checkbox"
      bind:checked={otSurveyRG4Checked}
      class="checkbox-target checkbox-style"
      on:click={handleOTSurvey4CheckboxClick}
    />
    <label
      for="add-ot-survey-passages-rg4-checkbox"
      class="pl-1 text-xl text-[#33445C] {isLoadingOTSurveyRG4 || otSurveyRG4SuccessMessage
        ? 'text-gray-400'
        : ''}">Add OT Survey RG4 Passages only (Isaiah to Malachi)</label
    >
    <div class="loader-container">
      {#if isLoadingOTSurveyRG4}
        <div class="loader"></div>
      {:else if otSurveyRG4SuccessMessage}
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
