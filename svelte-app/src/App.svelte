<script>
    import './App.css';

    let mediaRecorder;
    let audioChunks = [];
    let transcription = '';
    let isRecording = false;
    let isProcessing = false;
    let errorMessage = '';
    let question = '';
    let answer = '';

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            isRecording = true;
            errorMessage = '';
        } catch (error) {
            errorMessage = 'Error accessing microphone: ' + error.message;
        }
    }

    async function stopRecording() {
        mediaRecorder.stop();
        mediaRecorder.onstop = async () => {
            isRecording = false;
            isProcessing = true;
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('file', audioBlob, 'audio.wav');

            try {
                const response = await fetch('http://127.0.0.1:8000/transcribe', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                transcription = result.transcription;
                errorMessage = '';
            } catch (error) {
                errorMessage = 'Error during transcription: ' + error.message;
            } finally {
                isProcessing = false;
                audioChunks = [];
            }
        };
    }

    async function askQuestion() {
        try {
            const response = await fetch('http://127.0.0.1:8000/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question })
            });

            const result = await response.json();
            answer = result.answer;
            errorMessage = '';
        } catch (error) {
            errorMessage = 'Error during question processing: ' + error.message;
        }
    }
</script>

<h1>Record Audio and Transcribe</h1>
<button on:click={startRecording} disabled={isRecording || isProcessing}>Record</button>
<button on:click={stopRecording} disabled={!isRecording}>Stop</button>

{#if isProcessing}
    <p>Processing...</p>
{/if}

{#if errorMessage}
    <p class="error">{errorMessage}</p>
{/if}

{#if transcription}
    <p class="transcription">{transcription}</p>
{/if}

<h1>Ask a Question</h1>
<form on:submit|preventDefault={askQuestion}>
    <input type="text" bind:value={question} placeholder="Type your question here" required>
    <button type="submit">Ask</button>
</form>

{#if answer}
    <p class="answer">{answer}</p>
{/if}