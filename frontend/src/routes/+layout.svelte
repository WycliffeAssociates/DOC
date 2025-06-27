<script lang="ts">
  import '../app.pcss'
  import { env } from '$env/dynamic/public'
</script>

<slot />
<div class="footer">
  System version: {env.PUBLIC_DOC_VERSION}<br />
  Released on: {env.PUBLIC_DOC_BUILD_TIMESTAMP}
</div>

<style lang="postcss">
  .footer {
    margin-top: 12px;
    margin-left: 12px;
  }

  :global(li.target:has(input[type='checkbox']:checked)) {
    background: #e6eefb;
  }
  :global(div.target:has(input[type='checkbox']:checked)) {
    background: #e6eefb;
  }
  :global(div.target:has(input[type='radio']:checked)) {
    background: #e6eefb;
  }
  :global(div.target2:has(input[type='checkbox']:checked) + div) {
    color: #015ad9;
  }
  :global(div.target2:has(input[type='checkbox']:checked) + span) {
    color: #015ad9;
  }
  :global(div.target3:has(input[type='checkbox']:checked) + span) {
    color: #015ad9;
  }
  :global(input.checkbox-target[type='checkbox']:checked + span) {
    color: #015ad9;
  }
  :global(.checkbox-style) {
    @apply h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600;
  }
</style>
