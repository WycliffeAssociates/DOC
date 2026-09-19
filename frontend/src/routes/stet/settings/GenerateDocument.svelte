<script lang="ts">
  import { env } from '$env/dynamic/public'
  import DownloadButton from './DownloadButton.svelte'
  import { documentReadyStore, errorStore } from '$lib/stet/stores/NotificationStore'
  import {
    lang0CodeAndNameStore,
    lang1CodeAndNameStore,
    langCodesStore,
    langCountStore
  } from '$lib/stet/stores/LanguagesStore'
  import {
    emailStore,
    documentRequestKeyStore,
    settingsUpdatedStore,
    useIncreasedLineSpacingStore
  } from '$lib/stet/stores/SettingsStore'
  import { taskIdStore, taskStateStore } from '$lib/stet/stores/TaskStore'
  import { getCode } from '$lib/stet/utils'
  import LogRocket from 'logrocket'
  import TaskStatus from './TaskStatus.svelte'
  import ErrorAlertIcon from '$lib/ErrorAlertIcon.svelte'

  let apiRootUrl = env.PUBLIC_BACKEND_API_URL
  let fileServerUrl: string = env.PUBLIC_FILE_SERVER_URL

  async function poll(taskId: string): Promise<string | [string, string]> {
    console.log(`taskId in poll: ${taskId}`)
    let res = await fetch(`${apiRootUrl}/stet/task_status/${taskId}`, {
      method: 'GET'
    })
    let json = await res.json()
    let state = json?.state
    if (state === 'SUCCESS') {
      let result = json?.result
      return [state, result]
    }
    return state
  }

  $: generatingDocument = false

  async function generateDocument() {
    // Update some UI-related state
    generatingDocument = true
    $settingsUpdatedStore = false
    // Create the JSON structure to POST.
    let documentRequest = {
      lang0_code: getCode($lang0CodeAndNameStore),
      lang1_code: getCode($lang1CodeAndNameStore),
      email_address: $emailStore,
      use_increased_line_spacing: $useIncreasedLineSpacingStore
    }
    console.log('document request: ', JSON.stringify(documentRequest, null, 2))
    $errorStore = null
    $documentReadyStore = false
    $documentRequestKeyStore = ''
    let endpointUrl = `${apiRootUrl}/stet/documents_docx`
    const response = await fetch(endpointUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(documentRequest)
    })
    const data = await response.json()
    if (!response.ok) {
      console.error(`data.detail: ${data.detail}`)
      $errorStore = data.detail
    } else {
      console.log(`data: ${JSON.stringify(data)}`)
      const timerIntervalId = setInterval(async function () {
        // Poll the server for the task state and result
        let results = await poll(data.task_id)
        console.log(`results: ${results}`)
        $taskStateStore = Array.isArray(results) ? results[0] : results
        console.log(`$taskStateStore: ${$taskStateStore}`)
        if ($taskStateStore === 'SUCCESS' && Array.isArray(results) && results[1]) {
          let finishedDocumentRequestKey = results[1]
          console.log(`finishedDocumentReuestKey: ${finishedDocumentRequestKey}`)
          // Update some UI-related state
          $documentReadyStore = true
          $documentRequestKeyStore = finishedDocumentRequestKey
          $errorStore = null
          $taskStateStore = ''
          generatingDocument = false
          clearInterval(timerIntervalId)
        } else if ($taskStateStore === 'FAILURE') {
          console.log("We're sorry, an internal error occurred which we'll investigate.")
          // Update some UI-related state
          $errorStore =
            "We're sorry. An error occurred. The document you requested may not yet be supported or we may have experienced an internal problem which we'll investigate. Please try another document request."
          $taskStateStore = ''
          generatingDocument = false
          clearInterval(timerIntervalId)
        }
      }, 5000)
    }
  }

  // Reactively set/store email (for this session) and identify session to
  // LogRocket
  $: {
    // Deal with empty string case
    if ($emailStore && $emailStore === '') {
      $emailStore = null
      LogRocket.identify($documentRequestKeyStore)
      // Deal with undefined case
    } else if ($emailStore === undefined) {
      $emailStore = null
      LogRocket.identify($documentRequestKeyStore)
      // Deal with non-empty string
    } else if ($emailStore && $emailStore !== '') {
      $emailStore = $emailStore.trim()
      // The LogRocket init call has been moved to App.svelte to be earlier in
      // the loading process so that hopefully more of the session
      // is recorded.
      // Send email to LogRocket to identify session.
      LogRocket.identify($emailStore)
    }
  }

  let docxDownloadUrl: string
  $: docxDownloadUrl = `${fileServerUrl}/${$documentRequestKeyStore}.docx`

  // Warn user when they attempt to reload page or close tab
  window.addEventListener('beforeunload', (event) => {
    if (generatingDocument) {
      event.returnValue = `Are you sure you want to leave while your document is being generated?`
    }
  })
</script>

<div class="bg-white pb-4 pt-12">
  {#if $errorStore}
    <div class="bg-white">
      <ErrorAlertIcon />
      <div class="m-auto"><h3 class="text-center text-[#B85659]">Uh Oh...</h3></div>
      <div class="m-auto">
        <p class="text-xl text-[#B3B9C2]">
          Something went wrong. Please review your selections or contact tech support for
          assistance.
        </p>
      </div>
    </div>
  {:else if (!generatingDocument && !$documentReadyStore) || $settingsUpdatedStore}
    {#if $lang0CodeAndNameStore && $lang1CodeAndNameStore}
      <div class="pb-4">
        <button
          class="blue-gradient w-1/2 rounded-md p-4 text-center"
          on:click={() => generateDocument()}
        >
          <span class="text-xl text-white">Generate File</span>
        </button>
      </div>
    {:else}
      <div class="pb-4">
        <button class="gray-gradiant btn-disabled w-1/2 rounded-md p-4 text-center">
          <span class="text-xl text-[#b3b9c2]" style="color: #140e0866">Generate File</span>
        </button>
      </div>
    {/if}
  {:else}
    {#if !$documentReadyStore}
      <TaskStatus />
    {/if}
    {#if $documentReadyStore}
      <div class="bg-white">
        <div class="h-1 w-1/2 bg-[#F2F3F5]">
          <div class="blue-gradient-bar h-1" style="width: 100%" />
        </div>
        <div class="m-auto"><h3 class="text-xl text-[#82A93F]">Complete!</h3></div>
        <div class="m-auto mt-4">
          <DownloadButton buttonText="Download Docx" url={docxDownloadUrl} />
        </div>
        <div class="mt-4 text-[#33445C]">
          <p>
            Any missing fonts on your computer may be downloaded here:
            <span style="text-decoration-line: underline;">
              <a
                href="https://github.com/Bible-Translation-Tools/ScriptureAppBuilder-pipeline/tree/base/ContainerImage/home/fonts"
                target="_blank">fonts</a
              >
            </span>
          </p>
        </div>
        <div class="mt-4 text-xl text-[#33445C]">
          <p>
            Once you have downloaded and installed any missing fonts, select the document text which
            looks like little empty boxes (indicating a missing font), and change the font for that
            highlighted text to the appropriate installed font in Word, then save the Word document.
          </p>
        </div>
      </div>
    {:else}
      <button
        class="mb-4 mt-2 w-1/2 rounded-md
                    border border-[#E5E8EB] bg-[#F2F3F5] p-4
                    text-center text-xl text-[#B3B9C2] hover:bg-[#efefef]"
        disabled
      >
        Download
      </button>
      <p class="mt-4 text-xl italic text-[#B3B9C2]">
        We appreciate your patience as this can take several minutes to acquire and process all the
        books whose verses are referenced.
      </p>
    {/if}
  {/if}
</div>

<style lang="postcss">
  * :global(.gray-gradiant) {
    background:
      linear-gradient(0deg, rgba(20, 14, 8, 0.05), rgba(20, 14, 8, 0.05)),
      linear-gradient(0deg, rgba(20, 14, 8, 0), rgba(20, 14, 8, 0));
  }
  * :global(.gray-gradient:hover) {
    background:
      linear-gradient(0deg, rgba(20, 14, 8, 0.3), rgba(20, 14, 8, 0.3)),
      linear-gradient(0deg, rgba(20, 14, 8, 0.05), rgba(20, 14, 8, 0.05));
  }
  * :global(.blue-gradient) {
    background:
      linear-gradient(180deg, #1876fd 0%, #015ad9 100%), linear-gradient(0deg, #33445c, #33445c);
  }
  * :global(.blue-gradient-bar) {
    background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%);
  }
</style>
