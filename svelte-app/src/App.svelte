<script>
    import "./App.css";

    let mediaRecorder;
    let audioChunks = [];
    let transcription = "";
    let isRecording = false;
    let isProcessing = false;
    let errorMessage = "";
    let question = "";
    let answer = "";
    let storyText = "";
    let questionText = "";

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            isRecording = true;
            errorMessage = "";
        } catch (error) {
            errorMessage = "Error accessing microphone: " + error.message;
        }
    }

    async function stopRecording(endpoint) {
        mediaRecorder.stop();
        mediaRecorder.onstop = async () => {
            isRecording = false;
            isProcessing = true;
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            const formData = new FormData();
            formData.append("file", audioBlob, "audio.wav");

            try {
                const response = await fetch(endpoint, {
                    method: "POST",
                    body: formData,
                });

                const result = await response.json();
                if (endpoint.includes("transcribe")) {
                    transcription = result.transcription;
                } else if (endpoint.includes("ask")) {
                    answer = result.answer;
                }
                errorMessage = "";
            } catch (error) {
                errorMessage = "Error during transcription: " + error.message;
            } finally {
                isProcessing = false;
                audioChunks = [];
            }
        };
    }

    async function submitStory() {
        if (storyText.trim() === "") {
            errorMessage = "Please enter some text.";
            return;
        }

        isProcessing = true;
        errorMessage = "";
        try {
            const response = await fetch("http://127.0.0.1:8000/transcribe", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ text: storyText }),
            });

            const result = await response.json();
            transcription = result.transcription;
            storyText = "";
            errorMessage = "";
        } catch (error) {
            errorMessage = "Error during story submission: " + error.message;
        } finally {
            isProcessing = false;
        }
    }

    async function askQuestion() {
        if (questionText.trim() === "") {
            errorMessage = "Please enter some text.";
            return;
        }

        isProcessing = true;
        errorMessage = "";
        try {
            const response = await fetch("http://127.0.0.1:8000/ask", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ question: questionText }),
            });

            const result = await response.json();
            answer = result.answer;
            errorMessage = "";
        } catch (error) {
            errorMessage = "Error during question processing: " + error.message;
        } finally {
            isProcessing = false;
        }
    }
</script>

<h1>Record Your Stories</h1>
<div class="card-container">
    <div class="card">
        <div class="story-input">
            <h2>Type Your Story</h2>
            <textarea bind:value={storyText} placeholder="Type your story here"></textarea>
            <button on:click={submitStory} disabled={isProcessing}>Submit</button>
        </div>
        <div class="story-record">
            <h2>Voice Your Story</h2>
            <button on:click={() => startRecording()} disabled={isRecording || isProcessing}>Record</button>
            <button on:click={() => stopRecording("http://127.0.0.1:8000/transcribe")} disabled={!isRecording}>Stop</button>
            {#if isRecording}
                <div class="recording-indicator"></div>
            {/if}
        </div>
    </div>
</div>

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
<div class="card-container">
    <div class="card">
        <div class="question-input">
            <h2>Type Your Question</h2>
            <textarea bind:value={questionText} placeholder="Type your question here"></textarea>
            <button on:click={askQuestion} disabled={isProcessing}>Submit</button>
        </div>
        <div class="question-record">
            <h2>Voice Your Question</h2>
            <button on:click={() => startRecording()} disabled={isRecording || isProcessing}>Record</button>
            <button on:click={() => stopRecording("http://127.0.0.1:8000/ask")} disabled={!isRecording}>Stop</button>
            {#if isRecording}
                <div class="recording-indicator"></div>
            {/if}
        </div>
    </div>
</div>

{#if answer}
    <p class="answer">{answer}</p>
{/if}