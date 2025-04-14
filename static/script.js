function showScreen(id) {
  const screens = document.querySelectorAll('.container');
  screens.forEach(screen => screen.style.display = 'none');
  document.getElementById(id).style.display = 'block';

  if (id === 'encrypt-screen' || id === 'decrypt-screen') {
    populateDropdowns();
  }
}


let latestPayload = null;

function encryptSelectedFile() {
  const fileInput = document.getElementById('encrypt-input');
  const file = fileInput.files[0];

  if (!file) {
    alert("Please select a file to encrypt.");
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  fetch('/encrypt', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(payload => {
      latestPayload = payload;

      const downloadBtn = document.getElementById('download-payload-btn');
      downloadBtn.style.display = 'inline-block';

      downloadBtn.onclick = () => {
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        // Safely extract base filename without extension
        const nameParts = (payload.filename || "encrypted_output").split(".");
        const baseName = nameParts.length > 1 ? nameParts.slice(0, -1).join(".") : nameParts[0];
        const downloadName = baseName + "_encrypted.json";

        const a = document.createElement('a');
        a.href = url;
        a.download = downloadName;
        a.click();
        URL.revokeObjectURL(url);
      };
    })
    .catch(err => alert('Encryption failed: ' + err.message));
}


let decryptedBlobUrl = null;

function decryptSelectedFile() {
  const fileInput = document.getElementById("decrypt-input");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a payload to decrypt.");
    return;
  }

  const formData = new FormData();
  formData.append("payload", file);

  fetch("/decrypt", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error("Decryption failed: " + text);
        });
      }

      // Extract filename from Content-Disposition header
      const disposition = response.headers.get("Content-Disposition");
      const matches = disposition && disposition.match(/filename="(.+?)"/);
      let filename = matches?.[1] || "decrypted_output";

      // Extract MIME type
      const mimeType = response.headers.get("Content-Type") || "application/octet-stream";

      // Add extension if filename has none
      const mimeToExt = {
        "application/pdf": ".pdf",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "application/zip": ".zip",
        "text/plain": ".txt",
        "application/json": ".json",
        "video/mp4": ".mp4",
      };

      if (!filename.includes(".") && mimeToExt[mimeType]) {
        filename += mimeToExt[mimeType];
      }

      return response.blob().then((blob) => {
        decryptedBlobUrl = URL.createObjectURL(new Blob([blob], { type: mimeType }));

        const downloadBtn = document.getElementById("download-decrypted-btn");
        downloadBtn.style.display = "inline-block";

        downloadBtn.onclick = () => {
          const a = document.createElement("a");
          a.href = decryptedBlobUrl;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(decryptedBlobUrl);  
        };
      });
    })
    .catch((err) => alert(err.message));
}
