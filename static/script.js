document.addEventListener('paste', function(event) {
    let items = (event.clipboardData || event.originalEvent.clipboardData).items;
    for (let index in items) {
        let item = items[index];
        if (item.kind === 'file') {
            let blob = item.getAsFile();
            let formData = new FormData();
            formData.append('file', blob, 'clipboard_image.png');

            fetch(uploadUrl, {
                method: 'POST',
                body: formData
            }).then(response => response.text())
              .then(data => {
                  document.open();
                  document.write(data);
                  document.close();
              })
              .catch(error => console.error('Error:', error));
        }
    }
});

function resetForm() {
    if (file_path) {
        let formData = new FormData();
        formData.append('file_path', file_path);
        fetch(resetUrl, {
            method: 'POST',
            body: formData
        }).then(response => {
            window.location.href = indexUrl;
        }).catch(error => console.error('Error:', error));
    } else {
        window.location.href = indexUrl;
    }
}

// 드래그 앤 드랍 기능 추가
const dropZone = document.getElementById('drop-zone');

dropZone.addEventListener('dragover', (event) => {
    event.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (event) => {
    event.preventDefault();
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (event) => {
    event.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const formData = new FormData();
        formData.append('file', files[0]);

        fetch(uploadUrl, {
            method: 'POST',
            body: formData
        }).then(response => response.text())
          .then(data => {
              document.open();
              document.write(data);
              document.close();
          })
          .catch(error => console.error('Error:', error));
    }
});