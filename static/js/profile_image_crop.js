// static/js/profile_image_crop.js
document.addEventListener('DOMContentLoaded', function() {
    const profileInput = document.getElementById('profile_image');
    if (!profileInput) return;

    let cropper;
    const modalHtml = `
        <div class="modal fade" id="cropModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Crop Profile Picture</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <img id="crop-image" src="" style="max-width: 100%;">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="crop-save">Crop & Save</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const cropModal = new bootstrap.Modal(document.getElementById('cropModal'));

    profileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(ev) {
                const img = document.getElementById('crop-image');
                img.src = ev.target.result;
                cropModal.show();
                if (cropper) cropper.destroy();
                cropper = new Cropper(img, {
                    aspectRatio: 1,
                    viewMode: 1,
                    autoCropArea: 1,
                    dragMode: 'move',
                });
            };
            reader.readAsDataURL(file);
        }
    });

    document.getElementById('crop-save').addEventListener('click', function() {
        if (!cropper) return;
        const canvas = cropper.getCroppedCanvas({
            width: 500,
            height: 500,
        });
        canvas.toBlob(function(blob) {
            const formData = new FormData();
            formData.append('file', blob, 'profile.jpg');
            fetch('/upload-profile-image', {  // FIXED: now points to the correct route
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.CSRF_TOKEN   // FIXED: added CSRF token
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.filename) {
                    // Update profile image on page (optional)
                    location.reload(); // simple refresh
                }
            })
            .catch(err => console.error('Upload failed:', err));
        }, 'image/jpeg');
        cropModal.hide();
    });
});