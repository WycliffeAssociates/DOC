<style>
  :global(body) {
    font-family: Arial, Helvetica, sans-serif;
    background-color: #f3f3f3;
  }
  :global(*, *:before, *:after) {
    box-sizing: border-box;
  }
  :global(input[type='text'], input[type='select'], input[type='password'], input[type='number'], select) {
    padding: 5px;
    min-width: 30em;
  }
  .box {
    width: 100px;
    height: 100px;
    background-color: #ff4;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .fields {
    margin: 2em 0;
  }
  .fields label {
    display: block;
    margin-top: 1em;
  }
  .forms {
    margin: 2em 5em 2em 10em;
  }
  .container {
    display: flex;
  }
  .results {
    position: fixed;
    overflow: auto;
    right: 0;
    width: 40%;
    height: 100%;
    background-color: #def7f7;
    padding: 10% 3em;
  }
  .results pre {
    font-size: 1.2em;
  }
</style>

<script lang="ts">
  import { onMount } from 'svelte';

  let API_ROOT_URL = 'http://localhost:5005';

  let assemblyStrategies = [
    { id: 'book_language_order', label: 'Sort by book then by language' },
    { id: 'language_book_order', label: 'Sort by language, and then by book' },
  ];

  let langs0 = [];
  let langs1 = [];
  let langs2 = [];

  let lang0Code = '';
  let lang1Code = '';
  let lang2Code = '';
  let lang0ResourceTypes = [];
  let lang1ResourceTypes = [];
  let lang2ResourceTypes = [];
  let lang0ResourceCodes = [];
  let lang1ResourceCodes = [];
  let lang2ResourceCodes = [];
  let documentRequest = {
    assemblyStrategy: assemblyStrategies[0],
    email: null,
    lang0Code: lang0Code,
    lang0ResourceTypes: lang0ResourceTypes,
    lang0ResourceCodes: lang0ResourceCodes,
    lang1Code: lang1Code,
    lang1ResourceTypes: lang1ResourceTypes,
    lang1ResourceCodes: lang1ResourceCodes,
    lang2Code: lang2Code,
    lang2ResourceTypes: lang2ResourceTypes,
    lang2ResourceCodes: lang2ResourceCodes,
  };
  // Button will toggle this value
  let showAnotherLang = false;
  function handleAddLang() {
    showAnotherLang = true;
  }
  let showAnotherLang2 = false;
  function handleAddLang2() {
    showAnotherLang2 = true;
  }
  function isEmpty(str: string): boolean {
    return !str || str.trim().length === 0;
  }

  async function getLang0CodesAndNames() {
    const response = await fetch(API_ROOT_URL + '/language_codes_and_names');
    langs0 = await response.json();
  }

  onMount(async () => {
    // const response = await fetch(API_ROOT_URL + '/language_codes_and_names');
    // langs0 = await response.json();
    getLang0CodesAndNames();
  });

  // FIXME Consider more fully using promises rather than async/await/exceptions
  // Source: https://jessewarden.com/2021/06/why-i-dont-use-async-await.html
  // const getLang1CodesAndNames =>
  //    fetch(API_ROOT_URL + '/language_codes_and_names')
  //    .then( response => langs1 = response.json() ) // Here you'd maybe, see next line, return object from json instead of doing assignment to global.
  //    .then( json => {
  //        const something = json?.data?.something ?? []
  //        return something
  //     })
  //    .catch( error => console.log( "http failed: ", error)
  // NOTE Possibly after the function above is defined we would then await that
  // directly in the "html" template below rather than storing its value into
  // langs1

  async function getLang1CodesAndNames() {
    const response = await fetch(API_ROOT_URL + '/language_codes_and_names');
    langs1 = await response.json();
  }

  async function getLang2CodesAndNames() {
    const response = await fetch(API_ROOT_URL + '/language_codes_and_names');
    langs2 = await response.json();
  }
  async function getLang0ResourceTypes(langCode: string) {
    const response = await fetch(API_ROOT_URL + '/resource_types_for_lang/' + langCode);
    lang0ResourceTypes = await response.json();
  }
  async function getLang1ResourceTypes(langCode: string) {
    const response = await fetch(API_ROOT_URL + '/resource_types_for_lang/' + langCode);
    lang1ResourceTypes = await response.json();
  }

  async function getLang2ResourceTypes(langCode: string) {
    const response = await fetch(API_ROOT_URL + '/resource_types_for_lang/' + langCode);
    lang2ResourceTypes = await response.json();
  }
  async function getLang0ResourceCodes(langCode: string) {
    const response = await fetch(API_ROOT_URL + '/resource_codes_for_lang/' + langCode);
    lang0ResourceCodes = await response.json();
  }
  async function getLang1ResourceCodes(langCode: string) {
    const response = await fetch(API_ROOT_URL + '/resource_codes_for_lang/' + langCode);
    lang1ResourceCodes = await response.json();
  }
  async function getLang2ResourceCodes(langCode: string) {
    const response = await fetch(API_ROOT_URL + '/resource_codes_for_lang/' + langCode);
    lang2ResourceCodes = await response.json();
  }
  let finished_document_url = '';

  function reset() {
    Object.keys(documentRequest).forEach((key) => (documentRequest[key] = ''));
    hideWaitMessage();
    hideErrorMessage();
    langs0 = [];
    langs1 = [];
    langs2 = [];
    lang0Code = '';
    lang1Code = '';
    lang2Code = '';
    lang0ResourceTypes = [];
    lang1ResourceTypes = [];
    lang2ResourceTypes = [];
    lang0ResourceCodes = [];
    lang1ResourceCodes = [];
    lang2ResourceCodes = [];
    finished_document_url = '';
    getLang0CodesAndNames();
    documentRequest.email = null; // Be careful to set email to null as API expects a null rather than empty string if not provided
    document.getElementById('email').focus();
  }

  // Submit button will toggle this value
  $: waitMessage = false;
  function hideWaitMessage() {
    waitMessage = false;
  }
  function showWaitMessage() {
    waitMessage = true;
  }
  // Error will toggle this value
  $: errorMessage = false;
  $: errorMessageDetails = null;
  function hideErrorMessage() {
    errorMessage = false;
  }
  function showErrorMessage() {
    errorMessage = true;
  }

  async function submit() {
    let rr = [];
    // Create resource_requests for lang0
    for (let resourceCode of documentRequest.lang0ResourceCodes) {
      for (let resourceType of documentRequest.lang0ResourceTypes) {
        rr.push({ lang_code: documentRequest.lang0Code, resource_type: resourceType, resource_code: resourceCode });
      }
    }
    // Create resource_requests for lang1
    for (let resourceCode of documentRequest.lang1ResourceCodes) {
      for (let resourceType of documentRequest.lang1ResourceTypes) {
        rr.push({ lang_code: documentRequest.lang1Code, resource_type: resourceType, resource_code: resourceCode });
      }
    }
    // Create resource_requests for lang2
    for (let resourceCode of documentRequest.lang2ResourceCodes) {
      for (let resourceType of documentRequest.lang2ResourceTypes) {
        rr.push({ lang_code: documentRequest.lang2Code, resource_type: resourceType, resource_code: resourceCode });
      }
    }

    console.log(documentRequest.email);
    // Create the JSON structure to POST.
    let document_request = {
      email_address: !isEmpty(documentRequest.email) ? documentRequest.email.trim() : null,
      assembly_strategy_kind: documentRequest.assemblyStrategy,
      resource_requests: rr,
    };
    console.log(JSON.stringify(document_request, null, 2));
    // POST the DocumentRequest to the API
    if (errorMessage) {
      hideErrorMessage();
    }
    showWaitMessage();
    // try {
    fetch(API_ROOT_URL + '/documents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(document_request),
    })
      .then((response) => {
        if (!response.ok) {
          // return Promise.reject('Request failed error');
          throw new Error(response.json());
        }
      })
      .then((data) => {
        console.log(data);
        finished_document_url = data['finished_document_request_key'];
        hideWaitMessage();
      })
      .catch((err) => {
        console.error(JSON.stringify(err));
        hideWaitMessage();
        errorMessageDetails = JSON.stringify(err);
        showErrorMessage();
      });
  }
</script>

<div class="container">
  <div class="forms">
    <div>
      <h2>Document Request</h2>

      <form on:submit|preventDefault={submit}>
        <div class="fields">
          <label for="email">Email (Optional)</label>
          <input type="text" name="email" id="email" bind:value={documentRequest.email} />
        </div>
        <div>
          <h3>Please select the assembly strategy for this document</h3>
          <select bind:value={documentRequest.assemblyStrategy}>
            {#each assemblyStrategies as assemblyStrategy}
              <option value={assemblyStrategy.id}>{assemblyStrategy.label}</option>
            {/each}
          </select>
        </div>

        <div>
          <h3>Language #0</h3>
          {#await langs0}
            <p>...loading</p>
          {:then data}
            <select
              bind:value={documentRequest.lang0Code}
              name="lang0"
              id="lang0-select"
              on:change={() => getLang0ResourceTypes(documentRequest.lang0Code)}
            >
              {#each data as value}
                <option value={value[0]}>{value[1]}</option>
              {/each}
            </select>
          {:catch error}
            <p>{error.message}</p>
          {/await}
        </div>

        {#if !isEmpty(documentRequest.lang0Code)}
          <div>
            {#await lang0ResourceTypes}
              <p>...choose language #1 first</p>
            {:then data}
              <h3>Language #1 resource types</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={documentRequest.lang0ResourceTypes}
                    name="lang0ResourceTypes"
                    on:change={() => getLang0ResourceCodes(documentRequest.lang0Code)}
                    {value}
                  />
                  {value}
                </label>
              {/each}
            {:catch error}
              <p>{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(documentRequest.lang0Code) && documentRequest.lang0ResourceTypes.length > 0}
          <div>
            {#await lang0ResourceCodes}
              <p>...choose language #1 resource types first</p>
            {:then data}
              <h3>Language #1 resource codes</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={documentRequest.lang0ResourceCodes}
                    name="lang0ResourceCodes"
                    value={value[0]}
                    on:change={() => getLang1CodesAndNames()}
                  />
                  {value[1]}
                </label>
              {/each}
            {:catch error}
              <p>{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(documentRequest.lang0Code) && documentRequest.lang0ResourceTypes.length > 0 && documentRequest.lang0ResourceCodes.length > 0}
          <button disabled={showAnotherLang} on:click|preventDefault={handleAddLang}>Add another language</button>
        {/if}
        {#if showAnotherLang}
          <div>
            <h3>Language #2</h3>
            {#await langs1}
              <p>...loading</p>
            {:then data}
              <select
                bind:value={documentRequest.lang1Code}
                name="lang1"
                id="lang1-select"
                on:change={() => getLang1ResourceTypes(documentRequest.lang1Code)}
              >
                {#each data as value}
                  <option value={value[0]}>{value[1]}</option>
                {/each}
              </select>
            {:catch error}
              <p>{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(documentRequest.lang1Code)}
          <div>
            {#await lang1ResourceTypes}
              <p>...choose language #2 first</p>
            {:then data}
              <h3>Language #2 resource types</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={documentRequest.lang1ResourceTypes}
                    name="lang1ResourceTypes"
                    on:change={() => getLang1ResourceCodes(documentRequest.lang1Code)}
                    {value}
                  />
                  {value}
                </label>
              {/each}
            {:catch error}
              <p>{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(documentRequest.lang1Code) && documentRequest.lang1ResourceTypes.length > 0}
          <div>
            {#await lang1ResourceCodes}
              <p>...choose language #1 resource types first</p>
            {:then data}
              <h3>Language #2 resource codes</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={documentRequest.lang1ResourceCodes}
                    name="lang1ResourceCodes"
                    value={value[0]}
                    on:change={() => getLang2CodesAndNames()}
                  />
                  {value[1]}
                </label>
              {/each}
            {:catch error}
              <p>{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(documentRequest.lang1Code) && documentRequest.lang1ResourceTypes.length > 0 && documentRequest.lang1ResourceCodes.length > 0}
          <button disabled={showAnotherLang2} on:click|preventDefault={handleAddLang2}>Add another language</button>
        {/if}
        {#if showAnotherLang2}
          <div>
            <h3>Language #2</h3>
            {#await langs2}
              <p>...loading</p>
            {:then data}
              <!-- <h3>Language #2</h3> -->
              <select
                bind:value={documentRequest.lang2Code}
                name="lang2"
                id="lang2-select"
                on:change={() => getLang2ResourceTypes(documentRequest.lang2Code)}
              >
                {#each data as value}
                  <option value={value[0]}>{value[1]}</option>
                {/each}
              </select>
            {:catch error}
              <p>{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(documentRequest.lang2Code)}
          <div>
            {#await lang2ResourceTypes}
              <p>...choose language #2 first</p>
            {:then data}
              <h3>Language #2 resource types</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={documentRequest.lang2ResourceTypes}
                    name="lang2ResourceTypes"
                    on:change={() => getLang2ResourceCodes(documentRequest.lang2Code)}
                    {value}
                  />
                  {value}
                </label>
              {/each}
            {:catch error}
              <p>{error.message}</p>
            {/await}
          </div>
        {/if}
        {#if !isEmpty(documentRequest.lang2Code) && documentRequest.lang2ResourceTypes.length > 0}
          <div>
            {#await lang2ResourceCodes}
              <p>...choose language #2 resource types first</p>
            {:then data}
              <h3>Language #2 resource codes</h3>
              {#each data as value}
                <label>
                  <input
                    type="checkbox"
                    bind:group={documentRequest.lang2ResourceCodes}
                    name="lang2ResourceCodes"
                    value={value[0]}
                  />
                  {value[1]}
                </label>
              {/each}
            {:catch error}
              <p>{error.message}</p>
            {/await}
          </div>
        {/if}

        <div style="margin-top:3em">
          <button on:click|preventDefault={reset}>reset</button>
          <button type="submit">submit</button>
        </div>
      </form>

      {#if waitMessage}
        <div class="wait-message">
          <p>
            Thank you for submitting your document request. Please wait while the system generates your document. Note
            that, depending on the size of the document, this could take a while. A link will be presented to you in
            place of this message if the document is generated successfully. Thank you for your patience. If you have
            provided an email address above, the same link will also be sent to the email address provided.
          </p>
        </div>
      {/if}
      {#if errorMessage}
        <div class="error-message">
          <p>
            There was a problem handling your document request. The issue has been logged and we will take a look at it.
            We apologize for the inconvenience. Please try another selection by resetting the form and trying your new
            selection.
          </p>
        </div>
      {/if}
      {#if finished_document_url.length > 0}
        <div class="finished-document-url">
          <p>
            Your document is ready, please click
            <a href="{API_ROOT_URL}/pdfs/{finished_document_url}">here</a>
            to retrieve it.
          </p>
        </div>
      {/if}
    </div>
  </div>

  <!--   <div class="results"> -->
  <!--     <h3>Form Results</h3> -->
  <!--     <pre>{JSON.stringify(documentRequest, null, 2)}</pre> -->
  <!--   </div> -->
</div>
