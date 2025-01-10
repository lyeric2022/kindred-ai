<script>
    export let isProcessing = false;
    export let errorMessage = "";
  </script>
  
  {#if isProcessing}
    <p class="status">Processing...</p>
  {/if}
  
  {#if errorMessage}
    <p class="error">{errorMessage}</p>
  {/if}
  
  <style>
    .status {
      color: blue;
    }
    .error {
      color: red;
    }
  </style>
  