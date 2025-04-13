function showScreen(id) {
  const screens = document.querySelectorAll('.container');
  screens.forEach(screen => screen.style.display = 'none');
  document.getElementById(id).style.display = 'block';

  if (id === 'encrypt-screen' || id === 'decrypt-screen') {
    populateDropdowns();
  }
}

// Simulated file list
const uploadedFiles = ['example1.txt', 'report.pdf', 'notes.docx'];

function populateDropdowns() {
  const encryptDropdown = document.getElementById('encrypt-dropdown');
  const decryptDropdown = document.getElementById('decrypt-dropdown');

  encryptDropdown.innerHTML = '<option disabled selected>Select a file</option>';
  decryptDropdown.innerHTML = '<option disabled selected>Select a file</option>';

  uploadedFiles.forEach(file => {
    const option1 = document.createElement('option');
    const option2 = document.createElement('option');
    option1.value = option2.value = file;
    option1.text = option2.text = file;
    encryptDropdown.appendChild(option1);
    decryptDropdown.appendChild(option2);
  });
}

function handleUpload() {
  const fileInput = document.getElementById('upload-input');
  const file = fileInput.files[0];

  if (!file) {
    alert("No file selected.");
    return;
  }

  uploadedFiles.push(file.name);
  alert(`Uploaded: ${file.name}`);
  fileInput.value = ""; // Clear input
}

function encryptSelectedFile() {
  const selected = document.getElementById('encrypt-dropdown').value;
  if (!selected) return alert("Please select a file.");
  alert(`Encrypting file: ${selected}`);
}

function decryptSelectedFile() {
  const selected = document.getElementById('decrypt-dropdown').value;
  if (!selected) return alert("Please select a file.");
  alert(`Decrypting file: ${selected}`);
}
