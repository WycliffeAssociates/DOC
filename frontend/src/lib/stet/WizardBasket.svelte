<script lang="ts">
  import { goto } from '$app/navigation'
  import { page, navigating } from '$app/stores'
  import {
    lang0CodeAndNameStore,
    lang1CodeAndNameStore,
    langCodesStore,
    langCountStore,
    gatewayCodeAndNamesStore,
    heartCodeAndNamesStore
  } from '$lib/stet/stores/LanguagesStore'
  import { sourceLangRegExp, targetLangRegExp, getCode, getName } from '$lib/stet/utils'

  function uncheckGatewayLanguage(langCodeAndName: string) {
    if (langCodeAndName) {
      $gatewayCodeAndNamesStore = $gatewayCodeAndNamesStore.filter(
        (item) => getCode(item) != getCode(langCodeAndName)
      )
      $langCodesStore = $langCodesStore.filter(
        (item) => langCodeAndName && item != getCode(langCodeAndName)
      )
    }
    if (langCodeAndName && $lang0CodeAndNameStore && langCodeAndName === $lang0CodeAndNameStore) {
      $lang0CodeAndNameStore = ''
    }
    if (langCodeAndName && $lang1CodeAndNameStore && langCodeAndName === $lang1CodeAndNameStore) {
      $lang1CodeAndNameStore = ''
    }
    $langCountStore = $langCodesStore.length
  }

  function uncheckHeartLanguage(langCodeAndName: string) {
    if (langCodeAndName) {
      $heartCodeAndNamesStore = $heartCodeAndNamesStore.filter(
        (item) => getCode(item) != getCode(langCodeAndName)
      )
      $langCodesStore = $langCodesStore.filter((item) => item != getCode(langCodeAndName))
    }
    if (langCodeAndName && $lang0CodeAndNameStore && langCodeAndName === $lang0CodeAndNameStore) {
      $lang0CodeAndNameStore = ''
    }
    if (langCodeAndName && $lang1CodeAndNameStore && langCodeAndName === $lang1CodeAndNameStore) {
      $lang1CodeAndNameStore = ''
    }
    $langCountStore = $langCodesStore.length
  }

  $: console.log(
    `$lang0CodeAndNameStore: ${lang0CodeAndNameStore}, $lang1CodeAndNameStore: ${lang1CodeAndNameStore}`
  )
</script>

<div class="w-full flex-shrink-0 overflow-y-auto bg-[#f2f3f5] p-4">
  <h1 class="hidden py-4 pl-0 text-xl font-semibold text-[#33445C] sm:block">Your Selections</h1>
  {#if sourceLangRegExp.test($page.url.pathname)}
    <div class="my-2 flex items-center">
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M16.36 14C16.44 13.34 16.5 12.68 16.5 12C16.5 11.32 16.44 10.66 16.36 10H19.74C19.9 10.64 20 11.31 20 12C20 12.69 19.9 13.36 19.74 14H16.36ZM14.59 19.56C15.19 18.45 15.65 17.25 15.97 16H18.92C17.9512 17.6683 16.4141 18.932 14.59 19.56ZM14.34 14H9.66C9.56 13.34 9.5 12.68 9.5 12C9.5 11.32 9.56 10.65 9.66 10H14.34C14.43 10.65 14.5 11.32 14.5 12C14.5 12.68 14.43 13.34 14.34 14ZM12 19.96C11.17 18.76 10.5 17.43 10.09 16H13.91C13.5 17.43 12.83 18.76 12 19.96ZM8 8H5.08C6.03886 6.32721 7.5748 5.06149 9.4 4.44C8.8 5.55 8.35 6.75 8 8ZM5.08 16H8C8.35 17.25 8.8 18.45 9.4 19.56C7.57862 18.9317 6.04485 17.6677 5.08 16ZM4.26 14C4.1 13.36 4 12.69 4 12C4 11.31 4.1 10.64 4.26 10H7.64C7.56 10.66 7.5 11.32 7.5 12C7.5 12.68 7.56 13.34 7.64 14H4.26ZM12 4.03C12.83 5.23 13.5 6.57 13.91 8H10.09C10.5 6.57 11.17 5.23 12 4.03ZM18.92 8H15.97C15.657 6.76146 15.1936 5.5659 14.59 4.44C16.43 5.07 17.96 6.34 18.92 8ZM12 2C6.47 2 2 6.5 2 12C2 14.6522 3.05357 17.1957 4.92893 19.0711C5.85752 19.9997 6.95991 20.7362 8.17317 21.2388C9.38642 21.7413 10.6868 22 12 22C14.6522 22 17.1957 20.9464 19.0711 19.0711C20.9464 17.1957 22 14.6522 22 12C22 10.6868 21.7413 9.38642 21.2388 8.17317C20.7362 6.95991 19.9997 5.85752 19.0711 4.92893C18.1425 4.00035 17.0401 3.26375 15.8268 2.7612C14.6136 2.25866 13.3132 2 12 2Z"
          fill="#001533"
        />
      </svg>
      <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Source Language</h2>
    </div>
  {:else}
    <div class="my-2 flex items-center justify-between">
      <div class="flex items-center justify-between">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M16.36 14C16.44 13.34 16.5 12.68 16.5 12C16.5 11.32 16.44 10.66 16.36 10H19.74C19.9 10.64 20 11.31 20 12C20 12.69 19.9 13.36 19.74 14H16.36ZM14.59 19.56C15.19 18.45 15.65 17.25 15.97 16H18.92C17.9512 17.6683 16.4141 18.932 14.59 19.56ZM14.34 14H9.66C9.56 13.34 9.5 12.68 9.5 12C9.5 11.32 9.56 10.65 9.66 10H14.34C14.43 10.65 14.5 11.32 14.5 12C14.5 12.68 14.43 13.34 14.34 14ZM12 19.96C11.17 18.76 10.5 17.43 10.09 16H13.91C13.5 17.43 12.83 18.76 12 19.96ZM8 8H5.08C6.03886 6.32721 7.5748 5.06149 9.4 4.44C8.8 5.55 8.35 6.75 8 8ZM5.08 16H8C8.35 17.25 8.8 18.45 9.4 19.56C7.57862 18.9317 6.04485 17.6677 5.08 16ZM4.26 14C4.1 13.36 4 12.69 4 12C4 11.31 4.1 10.64 4.26 10H7.64C7.56 10.66 7.5 11.32 7.5 12C7.5 12.68 7.56 13.34 7.64 14H4.26ZM12 4.03C12.83 5.23 13.5 6.57 13.91 8H10.09C10.5 6.57 11.17 5.23 12 4.03ZM18.92 8H15.97C15.657 6.76146 15.1936 5.5659 14.59 4.44C16.43 5.07 17.96 6.34 18.92 8ZM12 2C6.47 2 2 6.5 2 12C2 14.6522 3.05357 17.1957 4.92893 19.0711C5.85752 19.9997 6.95991 20.7362 8.17317 21.2388C9.38642 21.7413 10.6868 22 12 22C14.6522 22 17.1957 20.9464 19.0711 19.0711C20.9464 17.1957 22 14.6522 22 12C22 10.6868 21.7413 9.38642 21.2388 8.17317C20.7362 6.95991 19.9997 5.85752 19.0711 4.92893C18.1425 4.00035 17.0401 3.26375 15.8268 2.7612C14.6136 2.25866 13.3132 2 12 2Z"
            fill="#001533"
          />
        </svg>
        <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Source Language</h2>
      </div>
      <button
        class="flex rounded bg-white px-4 py-2 text-xl text-[#33445c] hover:bg-[#efefef]"
        on:click={() => goto('/stet/source_languages')}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M3 17.4624V20.5024C3 20.7824 3.22 21.0024 3.5 21.0024H6.54C6.67 21.0024 6.8 20.9524 6.89 20.8524L17.81 9.94244L14.06 6.19244L3.15 17.1024C3.05 17.2024 3 17.3224 3 17.4624ZM20.71 7.04244C20.8027 6.94993 20.8762 6.84004 20.9264 6.71907C20.9766 6.59809 21.0024 6.46841 21.0024 6.33744C21.0024 6.20648 20.9766 6.07679 20.9264 5.95582C20.8762 5.83485 20.8027 5.72496 20.71 5.63244L18.37 3.29244C18.2775 3.19974 18.1676 3.12619 18.0466 3.07601C17.9257 3.02583 17.796 3 17.665 3C17.534 3 17.4043 3.02583 17.2834 3.07601C17.1624 3.12619 17.0525 3.19974 16.96 3.29244L15.13 5.12244L18.88 8.87244L20.71 7.04244Z"
            fill="#33445C"
          />
        </svg>
        <span class="ml-2"> Edit </span>
      </button>
    </div>
  {/if}
  {#if $lang0CodeAndNameStore}
    {#if sourceLangRegExp.test($page.url.pathname)}
      <div
        class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          <span>{getName($lang0CodeAndNameStore)}</span><span class="ml-2"
            >({getCode($lang0CodeAndNameStore)})</span
          >
        </div>
        <button
          on:click={() => {
            uncheckGatewayLanguage($lang0CodeAndNameStore)
            uncheckHeartLanguage($lang0CodeAndNameStore)
          }}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z"
              fill="#33445C"
            />
          </svg>
        </button>
      </div>
    {:else}
      <div
        class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          <span>{getName($lang0CodeAndNameStore)}</span><span class="ml-2"
            >({getCode($lang0CodeAndNameStore)})</span
          >
        </div>
      </div>
    {/if}
  {:else}
    <div class="rounded-lg bg-[#e5e8eb] p-6 text-xl text-[#66768b]">
      Selections will appear here once a source language is selected
    </div>
  {/if}
  {#if targetLangRegExp.test($page.url.pathname)}
    <div class="my-2 flex items-center">
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M16.36 14C16.44 13.34 16.5 12.68 16.5 12C16.5 11.32 16.44 10.66 16.36 10H19.74C19.9 10.64 20 11.31 20 12C20 12.69 19.9 13.36 19.74 14H16.36ZM14.59 19.56C15.19 18.45 15.65 17.25 15.97 16H18.92C17.9512 17.6683 16.4141 18.932 14.59 19.56ZM14.34 14H9.66C9.56 13.34 9.5 12.68 9.5 12C9.5 11.32 9.56 10.65 9.66 10H14.34C14.43 10.65 14.5 11.32 14.5 12C14.5 12.68 14.43 13.34 14.34 14ZM12 19.96C11.17 18.76 10.5 17.43 10.09 16H13.91C13.5 17.43 12.83 18.76 12 19.96ZM8 8H5.08C6.03886 6.32721 7.5748 5.06149 9.4 4.44C8.8 5.55 8.35 6.75 8 8ZM5.08 16H8C8.35 17.25 8.8 18.45 9.4 19.56C7.57862 18.9317 6.04485 17.6677 5.08 16ZM4.26 14C4.1 13.36 4 12.69 4 12C4 11.31 4.1 10.64 4.26 10H7.64C7.56 10.66 7.5 11.32 7.5 12C7.5 12.68 7.56 13.34 7.64 14H4.26ZM12 4.03C12.83 5.23 13.5 6.57 13.91 8H10.09C10.5 6.57 11.17 5.23 12 4.03ZM18.92 8H15.97C15.657 6.76146 15.1936 5.5659 14.59 4.44C16.43 5.07 17.96 6.34 18.92 8ZM12 2C6.47 2 2 6.5 2 12C2 14.6522 3.05357 17.1957 4.92893 19.0711C5.85752 19.9997 6.95991 20.7362 8.17317 21.2388C9.38642 21.7413 10.6868 22 12 22C14.6522 22 17.1957 20.9464 19.0711 19.0711C20.9464 17.1957 22 14.6522 22 12C22 10.6868 21.7413 9.38642 21.2388 8.17317C20.7362 6.95991 19.9997 5.85752 19.0711 4.92893C18.1425 4.00035 17.0401 3.26375 15.8268 2.7612C14.6136 2.25866 13.3132 2 12 2Z"
          fill="#001533"
        />
      </svg>
      <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Target Language</h2>
    </div>
  {:else}
    <div class="my-2 flex items-center justify-between">
      <div class="flex items-center justify-between">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M16.36 14C16.44 13.34 16.5 12.68 16.5 12C16.5 11.32 16.44 10.66 16.36 10H19.74C19.9 10.64 20 11.31 20 12C20 12.69 19.9 13.36 19.74 14H16.36ZM14.59 19.56C15.19 18.45 15.65 17.25 15.97 16H18.92C17.9512 17.6683 16.4141 18.932 14.59 19.56ZM14.34 14H9.66C9.56 13.34 9.5 12.68 9.5 12C9.5 11.32 9.56 10.65 9.66 10H14.34C14.43 10.65 14.5 11.32 14.5 12C14.5 12.68 14.43 13.34 14.34 14ZM12 19.96C11.17 18.76 10.5 17.43 10.09 16H13.91C13.5 17.43 12.83 18.76 12 19.96ZM8 8H5.08C6.03886 6.32721 7.5748 5.06149 9.4 4.44C8.8 5.55 8.35 6.75 8 8ZM5.08 16H8C8.35 17.25 8.8 18.45 9.4 19.56C7.57862 18.9317 6.04485 17.6677 5.08 16ZM4.26 14C4.1 13.36 4 12.69 4 12C4 11.31 4.1 10.64 4.26 10H7.64C7.56 10.66 7.5 11.32 7.5 12C7.5 12.68 7.56 13.34 7.64 14H4.26ZM12 4.03C12.83 5.23 13.5 6.57 13.91 8H10.09C10.5 6.57 11.17 5.23 12 4.03ZM18.92 8H15.97C15.657 6.76146 15.1936 5.5659 14.59 4.44C16.43 5.07 17.96 6.34 18.92 8ZM12 2C6.47 2 2 6.5 2 12C2 14.6522 3.05357 17.1957 4.92893 19.0711C5.85752 19.9997 6.95991 20.7362 8.17317 21.2388C9.38642 21.7413 10.6868 22 12 22C14.6522 22 17.1957 20.9464 19.0711 19.0711C20.9464 17.1957 22 14.6522 22 12C22 10.6868 21.7413 9.38642 21.2388 8.17317C20.7362 6.95991 19.9997 5.85752 19.0711 4.92893C18.1425 4.00035 17.0401 3.26375 15.8268 2.7612C14.6136 2.25866 13.3132 2 12 2Z"
            fill="#001533"
          />
        </svg>
        <h2 class="ml-2 text-xl font-semibold text-[#33445C]">Target Language</h2>
      </div>
      <button
        class="flex rounded bg-white px-4 py-2 text-xl text-[#33445c] hover:bg-[#efefef]"
        on:click={() =>
          $lang0CodeAndNameStore &&
          goto(`/stet/target_languages/${getCode($lang0CodeAndNameStore)}`)}
        disabled={!$lang0CodeAndNameStore}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M3 17.4624V20.5024C3 20.7824 3.22 21.0024 3.5 21.0024H6.54C6.67 21.0024 6.8 20.9524 6.89 20.8524L17.81 9.94244L14.06 6.19244L3.15 17.1024C3.05 17.2024 3 17.3224 3 17.4624ZM20.71 7.04244C20.8027 6.94993 20.8762 6.84004 20.9264 6.71907C20.9766 6.59809 21.0024 6.46841 21.0024 6.33744C21.0024 6.20648 20.9766 6.07679 20.9264 5.95582C20.8762 5.83485 20.8027 5.72496 20.71 5.63244L18.37 3.29244C18.2775 3.19974 18.1676 3.12619 18.0466 3.07601C17.9257 3.02583 17.796 3 17.665 3C17.534 3 17.4043 3.02583 17.2834 3.07601C17.1624 3.12619 17.0525 3.19974 16.96 3.29244L15.13 5.12244L18.88 8.87244L20.71 7.04244Z"
            fill="#33445C"
          />
        </svg>
        <span class="ml-2"> Edit </span>
      </button>
    </div>
  {/if}
  {#if $lang1CodeAndNameStore && typeof $lang1CodeAndNameStore === 'string'}
    {#if targetLangRegExp.test($page.url.pathname)}
      <div
        class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          <span>{getName($lang1CodeAndNameStore)}</span><span class="ml-2"
            >({getCode($lang1CodeAndNameStore)})</span
          >
        </div>
        <button
          on:click={() => {
            uncheckGatewayLanguage($lang1CodeAndNameStore)
            uncheckHeartLanguage($lang1CodeAndNameStore)
          }}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C6.47 2 2 6.47 2 12C2 17.53 6.47 22 12 22C17.53 22 22 17.53 22 12C22 6.47 17.53 2 12 2ZM16.3 16.3C16.2075 16.3927 16.0976 16.4663 15.9766 16.5164C15.8557 16.5666 15.726 16.5924 15.595 16.5924C15.464 16.5924 15.3343 16.5666 15.2134 16.5164C15.0924 16.4663 14.9825 16.3927 14.89 16.3L12 13.41L9.11 16.3C8.92302 16.487 8.66943 16.592 8.405 16.592C8.14057 16.592 7.88698 16.487 7.7 16.3C7.51302 16.113 7.40798 15.8594 7.40798 15.595C7.40798 15.4641 7.43377 15.3344 7.48387 15.2135C7.53398 15.0925 7.60742 14.9826 7.7 14.89L10.59 12L7.7 9.11C7.51302 8.92302 7.40798 8.66943 7.40798 8.405C7.40798 8.14057 7.51302 7.88698 7.7 7.7C7.88698 7.51302 8.14057 7.40798 8.405 7.40798C8.66943 7.40798 8.92302 7.51302 9.11 7.7L12 10.59L14.89 7.7C14.9826 7.60742 15.0925 7.53398 15.2135 7.48387C15.3344 7.43377 15.4641 7.40798 15.595 7.40798C15.7259 7.40798 15.8556 7.43377 15.9765 7.48387C16.0975 7.53398 16.2074 7.60742 16.3 7.7C16.3926 7.79258 16.466 7.90249 16.5161 8.02346C16.5662 8.14442 16.592 8.27407 16.592 8.405C16.592 8.53593 16.5662 8.66558 16.5161 8.78654C16.466 8.90751 16.3926 9.01742 16.3 9.11L13.41 12L16.3 14.89C16.68 15.27 16.68 15.91 16.3 16.3Z"
              fill="#33445C"
            />
          </svg>
        </button>
      </div>
    {:else}
      <div
        class="mt-2 flex w-full items-center justify-between
                 rounded-lg bg-white p-4 text-xl text-[#66768B]"
      >
        <div>
          <span>{getName($lang1CodeAndNameStore)}</span><span class="ml-2"
            >({getCode($lang1CodeAndNameStore)})</span
          >
        </div>
      </div>
    {/if}
  {:else}
    <div class="rounded-lg bg-[#e5e8eb] p-6 text-xl text-[#66768b]">
      Selections will appear here once a target language is selected
    </div>
  {/if}
</div>
