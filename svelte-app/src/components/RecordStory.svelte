<script>
    let storyText = "";
    let isProcessing = false;
    let isRecording = false;
    let errorMessage = "";
    let transcription = "";
    let audioChunks = [];
    let mediaRecorder;
    let audioFile = null;
  
    async function startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
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
          transcription = result.transcription;
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
      } catch (error) {
        errorMessage = "Error during story submission: " + error.message;
      } finally {
        isProcessing = false;
      }
    }
  
    async function uploadAudio() {
      if (!audioFile) {
        errorMessage = "Please select an audio file to upload.";
        return;
      }
  
      isProcessing = true;
      try {
        const formData = new FormData();
        formData.append("file", audioFile);
  
        const response = await fetch("http://127.0.0.1:8000/tts/upload", {
          method: "POST",
          body: formData,
        });
  
        if (response.ok) {
          errorMessage = "";
        } else {
          errorMessage = "Error during audio upload.";
        }
      } catch (error) {
        errorMessage = "Error during audio upload: " + error.message;
      } finally {
        isProcessing = false;
      }
    }
  
    function handleFileChange(event) {
      audioFile = event.target.files[0];
    }
  </script>
  
  <h1>Record Stories</h1>
  <div class="card-container">
    <div class="card">
      <div class="story-input">
        <h2>Type Your Story</h2>
        <textarea bind:value={storyText} placeholder="Type your story here"></textarea>
        <button on:click={submitStory} disabled={isProcessing}>Submit</button>
      </div>
      <div class="story-record">
        <h2>Voice Your Story</h2>
        <button on:click={startRecording} disabled={isRecording || isProcessing}>Record</button>
        <button on:click={() => stopRecording("http://127.0.0.1:8000/transcribe")} disabled={!isRecording}>Stop</button>
        {#if isRecording}
          <div class="recording-indicator"></div>
        {/if}
      </div>
      <div class="audio-upload">
        <h2>Upload Your Voice Audio</h2>
        <input type="file" accept="audio/*" on:change={handleFileChange} />
        <button on:click={uploadAudio} disabled={isProcessing}>Upload</button>
      </div>
    </div>
  </div>