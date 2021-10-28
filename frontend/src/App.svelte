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
    right: 0;
    width: 50%;
    height: 100%;
    background-color: #def7f7;
    padding: 10% 3em;
  }
  .results pre {
    font-size: 1.2em;
  }

</style>

<script lang="ts">
  // import { onMount } from 'svelte';
  // import slugify from 'slugify';
  // import ResourceRequest from './ResourceRequest.svelte';

  // let conferencing = [
  //   { id: '1', label: 'Zoom' },
  //   { id: '2', label: 'Hangouts' },
  //   { id: '3', label: 'Skype' },
  // ];

  // const frameworks = ['React', 'Svelte', 'Vue'];
  // const frameworks = [
  //   { id: 1, name: 'React.js' },
  //   { id: 2, name: 'Svelte.js' },
  //   { id: 3, name: 'Vue.js' },
  //   { id: 4, name: 'Marko.js' },
  // ];

  // let username = 'jane';

  // let values = {
  //   username: 'jane',
  //   startYear: 1999,
  //   company: '',
  //   slug: '',
  //   conferencing: 'hangouts',
  //   dynamic: conferencing[2],
  //   framework: 'Svelte',
  //   reactiveFrameworks: 'Vue',
  //   agree: true,
  //   tools: [],
  // };

  import { onMount } from 'svelte';
  // let characterName;
  let langCodesAndNames: { [string]: string };

  //  onMount(async () => {
  //    const response = await fetch('http://swapi.dev/api/people/1');
  //    const character = await response.json();
  //    characterName = character.name;
  //  });

  let API_BASE = 'http://localhost:5005';

  onMount(async () => {
    const response = await fetch('http://localhost:5005/language_codes_and_names');
    const data = await response.json();
    // console.log(data);
    //    for (let key in data) {
    //      let value = data[key];
    //      // Use `key` and `value`
    //    }
    // langCodesAndNames = Object.keys(data).forEach((key) => {
    //  key: data[key];
    // });
    langCodesAndNames = data;

    console.log('About to write langCodesAndNames to console');
    console.log(langCodesAndNames);
    // Object.keys(langCodesAndNames).forEach((key) => console.log(langCodesAndNames[key]));
    // console.log(typeof langCodesAndNames);
  });

  //  async function getLangCodes() {
  //    const response = await fetch('http://localhost:5005/language_codes');
  //    if (!response.ok) throw new Error(await response.text());
  //    console.log(response.json());
  //    return response.json();
  //  }

  let assemblyStrategies = [
    { id: 'book_language', label: 'Sort by book then by language' },
    { id: 'language_book', label: 'Sort by language, and then by book' },
  ];

  // let languages = [
  //   // { id: 'en', label: 'English' },
  //   // { id: 'es-419', label: 'Spanish' },
  //   // { id: 'pt-br', label: 'Portuguese' },
  // ];

  // let resource_types = [
  //   { id: 'ulb', label: 'English' },
  //   { id: 'es-419', label: 'Spanish' },
  //   { id: 'pt-br', label: 'Portuguese' },
  // ];

  let resourceRequest = {
    lang_code: '',
    resource_type: '',
    resource_code: '',
  };

  // function addResourceRequest(resourceRequest) {
  //   documentRequest.resourceRequests.push(resourceRequest);
  //   // This next line is required by Svelte to update an array/list of objects
  //   // Source: https://svelte.dev/tutorial/updating-arrays-and-objects
  //   documentRequest.resourceRequest = documentRequest.resourceRequest;
  // }

  let documentRequest = {
    assemblyStrategy: assemblyStrategies[0],
    emailAddress: '',
    resourceRequests: [],
  };

  const reset = () => Object.keys(documentRequest).forEach((key) => (documentRequest[key] = ''));
  const submit = () => alert(JSON.stringify(documentRequest, null, 2));

  // let box = null;

  // onMount(() => {
  //   var colors = ['#F99', '#9F9', '#99F', '#FF9', '#F9F'];

  //   setInterval(() => {
  //     let random = Math.floor(Math.random() * colors.length);
  //     let color = colors[random];
  //     box.style.background = color;
  //     box.innerHTML = color;
  //   }, 1000);
  // });

  // $: values.slug = slugify(values.company, { lower: true });

</script>

<div class="container">
  <div class="forms">
    <!-- <h2>Component bind</h2> -->
    <!-- <div class="box" bind:this={box}>color</div> -->
    <!-- <div> -->
    <!--   <h2>Simple two-way bind</h2> -->
    <!--   <form> -->
    <!--     <div><input type="text" name="username" bind:value={username} /></div> -->
    <!--     <div><input type="text" name="repeat" bind:value={username} /></div> -->
    <!--     <p>username <code>{username}</code></p> -->
    <!--     <button on:click|preventDefault={() => (username = '')}>reset</button> -->
    <!--   </form> -->
    <!-- </div> -->

    <div>
      <!-- {characterName} -->
      <!-- {languageCodes} -->
      <h2>Document Request</h2>

      <form on:submit|preventDefault={submit}>
        <div class="fields">
          <!--   <label for="username">Username</label> -->
          <!--   <input type="text" name="username" bind:value={values.username} /> -->

          <label for="email">Email</label>
          <input type="text" name="email" bind:value={documentRequest.email} />

          <!--   <label for="password">Password</label> -->
          <!--   <input type="password" name="password" bind:value={values.password} /> -->

          <!--   <label for="company">Company name</label> -->
          <!--   <input type="text" name="company" bind:value={values.company} /> -->

          <!--   <label for="slug">Slug</label> -->
          <!--   <input type="text" name="slug" bind:value={values.slug} /> -->

          <!--   <label for="startYear">Start year</label> -->
          <!--   <input type="number" name="startYear" bind:value={values.startYear} /> -->
        </div>

        <!-- <div> -->
        <!--   <h3>Simple select bind with static values</h3> -->
        <!--   <select bind:value={values.conferencing}> -->
        <!--     <option value="" /> -->
        <!--     <option value="zoom">Zoom.us</option> -->
        <!--     <option value="hangouts">Google Hangouts</option> -->
        <!--     <option value="skype">Microsoft Skype</option> -->
        <!--   </select> -->
        <!-- </div> -->

        <!-- <div> -->
        <!--   <h3>Dynamic select bind with objects</h3> -->
        <!--   <select bind:value={values.dynamic}> -->
        <!--     {#each conferencing as conference} -->
        <!--       <option value={conference}>{conference.label}</option> -->
        <!--     {/each} -->
        <!--   </select> -->
        <!-- </div> -->

        <div>
          <h3>Please select the assembly strategy for this document</h3>
          <select bind:value={documentRequest.assemblyStrategy}>
            {#each assemblyStrategies as assemblyStrategy}
              <option value={assemblyStrategy}>{assemblyStrategy.label}</option>
            {/each}
          </select>
        </div>

        <div>
          <h3>Here are the language, name, resource types data</h3>
          {#await langCodesAndNames}
            <p>...loading</p>
          {:then data}
            <p>Here is your data: {data}</p>
            <!-- {#each data as {row}} -->
            <!--   <div>{row}</div> -->
            <!-- {/each} -->
          {:catch error}
            <p>{error.message}</p>
          {/await}
        </div>

        <!-- <div> -->
        <!--   <h3>Dynamic multiple select bind with objects</h3> -->
        <!--   <select multiple bind:value={values.tools}> -->
        <!--     {#each conferencing as conference} -->
        <!--       <option value={conference}>{conference.label}</option> -->
        <!--     {/each} -->
        <!--   </select> -->
        <!-- </div> -->

        <!-- <div> -->
        <!--   <h3>Static radio button bind</h3> -->
        <!--   <label> <input type="radio" bind:group={values.framework} value="React" /> React </label> -->
        <!--   <label> <input type="radio" bind:group={values.framework} value="Svelte" /> Svelte </label> -->
        <!--   <label> <input type="radio" bind:group={values.framework} value="Vue" /> Vue </label> -->
        <!-- </div> -->

        <!-- <div> -->
        <!--   <h3>Dynamic radio button bind</h3> -->
        <!--   {#each frameworks as framework} -->
        <!--     <label> -->
        <!--       <input type="radio" bind:group={values.reactiveFrameworks} value={framework} /> -->
        <!--       {framework.name} -->
        <!--     </label> -->
        <!--   {/each} -->
        <!-- </div> -->

        <!-- <label> <input type="checkbox" bind:checked={documentRequest.agree} /> I am not a robot </label> -->

        <!-- <div> -->
        <!--   <h3>Component bind</h3> -->
        <!--   <ResourceRequest bind:order={values.resourceRequest} bind:amount={values.numberOfHotdogs} /> -->
        <!-- </div> -->

        <div style="margin-top:3em">
          <button on:click|preventDefault={reset}>reset</button>
          <button type="submit">submit</button>
        </div>
      </form>
    </div>
  </div>

  <div class="results">
    <h3>Complex Form Results</h3>
    <pre>{JSON.stringify(documentRequest, null, 2)}</pre>
  </div>
</div>
