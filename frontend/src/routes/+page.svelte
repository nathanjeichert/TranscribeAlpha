<script>
  let case_name = '';
  let case_number = '';
  let firm_name = '';
  let input_date = '';
  let input_time = '';
  let location = '';
  let speaker_names = '';
  let file;
  let transcript = '';
  let docx = '';
  let loading = false;

  async function submit() {
    if (!file) return;
    loading = true;
    const data = new FormData();
    data.append('case_name', case_name);
    data.append('case_number', case_number);
    data.append('firm_name', firm_name);
    data.append('input_date', input_date);
    data.append('input_time', input_time);
    data.append('location', location);
    if (speaker_names) data.append('speaker_names', speaker_names);
    data.append('file', file);
    const resp = await fetch('/api/transcribe', { method: 'POST', body: data });
    if (resp.ok) {
      const result = await resp.json();
      transcript = result.transcript;
      docx = result.docx_base64;
    } else {
      alert('Error generating transcript');
    }
    loading = false;
  }
</script>

<style>
  main { max-width: 800px; margin: 0 auto; font-family: system-ui, sans-serif; padding: 2rem; }
  h1 { text-align: center; margin-bottom: 1.5rem; }
  form { display: grid; gap: 0.75rem; }
  label { display: flex; flex-direction: column; font-weight: 600; }
  input[type='text'], input[type='date'], input[type='time'], input[type='file'] { padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; }
  button { padding: 0.6rem 1.2rem; border: none; background-color: #1b64d6; color: white; border-radius: 4px; cursor: pointer; }
  button:disabled { opacity: 0.6; cursor: not-allowed; }
  pre { white-space: pre-wrap; background: #f7f7f7; padding: 1rem; border-radius: 4px; }
  .download { margin-top: 1rem; display: inline-block; }
</style>

<main>
  <h1>Gemini Legal Transcript Generator</h1>
  <form on:submit|preventDefault={submit}>
    <label>Case Name<input bind:value={case_name} type="text" /></label>
    <label>Case Number<input bind:value={case_number} type="text" /></label>
    <label>Firm or Organization Name<input bind:value={firm_name} type="text" /></label>
    <label>Date<input bind:value={input_date} type="date" /></label>
    <label>Time<input bind:value={input_time} type="time" /></label>
    <label>Location<input bind:value={location} type="text" /></label>
    <label>Speaker Names (JSON list or blank)<input bind:value={speaker_names} type="text" /></label>
    <label>Audio/Video File<input type="file" on:change={(e)=>file=e.target.files[0]} required /></label>
    <button type="submit" disabled={loading}>{loading ? 'Transcribing...' : 'Generate Transcript'}</button>
  </form>

  {#if transcript}
    <h2>Transcript</h2>
    <pre>{transcript}</pre>
    {#if docx}
      <a class="download" download="transcript.docx" href={`data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,${docx}`}>Download DOCX</a>
    {/if}
  {/if}
</main>
