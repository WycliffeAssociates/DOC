<script lang="ts">
  import type { AssemblyStrategy } from '../types'
  import Switch from './Switch.svelte'
  import {
    layoutForPrintStore,
    assemblyStrategyKindStore,
    generatePdfStore,
    generateEpubStore,
    generateDocxStore,
    emailStore
  } from '../stores/SettingsStore'
  import { lang1CodeStore } from '../stores/LanguagesStore'
  import GenerateDocument from './GenerateDocument.svelte'

  let bookLanguageOrderStrategy: AssemblyStrategy = {
    id: 'blo',
    label: <string>import.meta.env.VITE_BOOK_LANGUAGE_ORDER_LABEL
  }
  let languageBookOrderStrategy: AssemblyStrategy = {
    id: 'lbo',
    label: <string>import.meta.env.VITE_LANGUAGE_BOOK_ORDER_LABEL
  }
  let assemblyStrategies = [bookLanguageOrderStrategy, languageBookOrderStrategy]

  const assemblyStrategyHeader = <string>import.meta.env.VITE_ASSEMBLY_STRATEGY_HEADER

  $: console.log(`$assemblyStrategyKindStore: ${$assemblyStrategyKindStore}`)
</script>

<h3 class="bg-white text-secondary-content text-lg pb-8 pt-2 pl-2">
  Interleave Settings
</h3>
<ul>
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <span class="text-primary-content">Print Optimization</span>
      <Switch bind:checked={$layoutForPrintStore} id="layout-for-print-store" />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will remove extra whitespace</span
      >
    </div>
  </li>
  {#if $lang1CodeStore}
    <li class="bg-white p-2">
      <div class="flex justify-between">
        <span class="text-primary-content">{assemblyStrategyHeader}</span>
        <select bind:value={$assemblyStrategyKindStore} name="assemblyStrategy">
          {#each assemblyStrategies as assemblyStrategy}
            <option value={assemblyStrategy.id}
              ><span class="text-primary-content">{assemblyStrategy.label}</span></option
            >
          {/each}
        </select>
      </div>
      <div>
        <span class="text-sm text-neutral-content"
          ><p>
            Choosing 'Mix' will interleave the content of two languages verse by verse.
          </p>
          <p>
            Choosing 'Separate' will keep the content separated by language per book.
          </p></span
        >
      </div>
    </li>
  {/if}
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <span class="text-primary-content">Generate PDF</span>
      <Switch bind:checked={$generatePdfStore} id="generate-pdf-store" />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Enabling this option will generate a PDF of the document.</span
      >
    </div>
  </li>
  {#if $assemblyStrategyKindStore === languageBookOrderStrategy.id}
    <li class="bg-white p-2">
      <div class="flex justify-between">
        <span class="text-primary-content">Generate Epub</span>
        <Switch bind:checked={$generateEpubStore} id="generate-epub-store" />
      </div>
      <div>
        <span class="text-sm text-neutral-content"
          >Enabling this option will generate an ePub of the document.</span
        >
      </div>
    </li>
    <li class="bg-white p-2">
      <div class="flex justify-between">
        <span class="text-primary-content">Generate Docx</span>
        <Switch bind:checked={$generateDocxStore} id="generate-docx-store" />
      </div>
      <div>
        <span class="text-sm text-neutral-content"
          >Enabling this option will generate a Docx of the document.</span
        >
      </div>
    </li>
  {/if}
  <li class="bg-white p-2">
    <div class="flex justify-between">
      <label for="email" class="text-primary-content"
        >{import.meta.env.VITE_EMAIL_LABEL}</label
      >
      <input
        type="text"
        name="email"
        id="email"
        bind:value={$emailStore}
        placeholder="Type email address here (optional)"
        class="input input-bordered bg-white w-full max-w-xs"
      />
    </div>
    <div>
      <span class="text-sm text-neutral-content"
        >Providing an email is optional and not required. If you provide an email address
        the system will send the download links for your generated document to your email
        address in addition to showing them on this page.</span
      >
    </div>
  </li>
</ul>
<GenerateDocument />