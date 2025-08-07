let selectedCertificate = null;

function sendPresetMessage(message) {
  if (selectedCertificate) {
    sendMessageToRasa(`/inform{{"certificate_type": "${selectedCertificate}"}}`);
  }
  sendMessageToRasa(message);
}

function selectCertificate(certName) {
  selectedCertificate = certName;
  sendMessageToRasa(`/inform{{"certificate_type": "${certName}"}}`);
}

// Modify HTML sidebar items like this:
document.querySelectorAll(".sidebar-item").forEach(item => {
  item.addEventListener("click", () => {
    const certText = item.innerText.split('\n')[0].trim();
    selectCertificate(certText);
  });
});
