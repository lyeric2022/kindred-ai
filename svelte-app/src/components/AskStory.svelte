<script>
    let questionText = "";
    let answer = "";
    let isProcessing = false;
    let isRecording = false;
    let errorMessage = "";
    let audioChunks = [];
    let mediaRecorder;
    let audioFile = null;

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
                answer = result.answer;
                errorMessage = "";
            } catch (error) {
                errorMessage = "Error during processing: " + error.message;
            } finally {
                isProcessing = false;
                audioChunks = [];
            }
        };
    }

    async function askQuestion() {
        if (questionText.trim() === "") {
            errorMessage = "Please enter some text.";
            return;
        }

        isProcessing = true;
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
        } catch (error) {
            errorMessage = "Error during question submission: " + error.message;
        } finally {
            isProcessing = false;
        }
    }

    async function synthesizeAnswer() {
        if (!answer) {
            errorMessage = "No answer to synthesize.";
            return;
        }

        isProcessing = true;
        try {
            const response = await fetch(
                "http://127.0.0.1:8000/tts/synthesize",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ gen_text: answer }),
                },
            );

            const result = await response.json();
            if (response.ok) {
                const audio = new Audio(result.audio_file);
                audio.play();
                errorMessage = "";
            } else {
                errorMessage = "Error during TTS synthesis: " + result.detail;
            }
        } catch (error) {
            errorMessage = "Error during TTS synthesis: " + error.message;
        } finally {
            isProcessing = false;
        }
    }
</script>

<h1>Ask a Question</h1>
<div class="card-container">
    <div class="card">
        <div class="question-input">
            <h2>Type Your Question</h2>
            <textarea
                bind:value={questionText}
                placeholder="Type your question here"
            ></textarea>
            <button on:click={askQuestion} disabled={isProcessing}
                >Submit</button
            >
        </div>
        <div class="question-record">
            <h2>Voice Your Question</h2>
            <button
                on:click={startRecording}
                disabled={isRecording || isProcessing}>Record</button
            >
            <button
                on:click={() => stopRecording("http://127.0.0.1:8000/ask")}
                disabled={!isRecording}>Stop</button
            >
            {#if isRecording}
                <div class="recording-indicator"></div>
            {/if}
        </div>
        <div class="synthesize-answer">
            <h2>Synthesize Answer</h2>
            <button on:click={synthesizeAnswer} disabled={isProcessing}
                >Synthesize</button
            >
        </div>
        {#if answer}
            <p class="answer">{answer}</p>
        {/if}
    </div>
</div>
