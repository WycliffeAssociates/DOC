<script lang="ts">
  import '../../app.pcss'
  import { env } from '$env/dynamic/public'
</script>

<slot />

<style lang="postcss">
  .footer {
    margin-top: 12px;
    margin-left: 12px;
  }
</style>
