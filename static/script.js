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

  if (!file) return alert("Please select a file to encrypt.");

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
        const a = document.createElement('a');
        a.href = url;
        a.download = "encrypted_output";
        a.click();
        URL.revokeObjectURL(url);
      };
    })
    .catch(err => alert('Encryption failed: ' + err.message));
}

let decryptedBlobUrl = null;

async function decryptSelectedFile() {
  const fileInput = document.getElementById("decrypt-input");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a payload to decrypt.");
    return;
  }

  const formData = new FormData();
  formData.append("payload", file);

  try {
    const response = await fetch("/decrypt", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error("Decryption failed: " + errorText);
    }

    const blob = await response.blob();
    decryptedBlobUrl = URL.createObjectURL(blob);

    const downloadBtn = document.getElementById("download-decrypted-btn");
    downloadBtn.style.display = "inline-block";

    // Set up click behavior
    downloadBtn.onclick = () => {
      const a = document.createElement("a");
      a.href = decryptedBlobUrl;
      a.download = "decrypted_output";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    };
  } catch (err) {
    alert(err.message);
  }
}
