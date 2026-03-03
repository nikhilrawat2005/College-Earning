// static/js/forms.js
document.addEventListener('DOMContentLoaded', function() {
    // ===== PASSWORD TOGGLE =====
    const togglePassword = (buttonId, inputId) => {
        const btn = document.getElementById(buttonId);
        const input = document.getElementById(inputId);
        if (btn && input) {
            btn.addEventListener('click', function() {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                this.querySelector('i').classList.toggle('fa-eye');
                this.querySelector('i').classList.toggle('fa-eye-slash');
            });
        }
    };

    togglePassword('togglePassword', 'password');
    togglePassword('toggleConfirmPassword', 'confirmPassword');
    togglePassword('toggleOldPassword', 'oldPassword');
    togglePassword('toggleNewPassword', 'newPassword');

    // ===== PHONE NUMBER PREFIX =====
    const phoneInput = document.querySelector('input[name="phone_number"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
        });
    }

    // ===== DYNAMIC SECTION DROPDOWN =====
    const branchSelect = document.getElementById('branchSelect');
    const sectionContainer = document.getElementById('sectionInput')?.parentNode;
    let sectionInput = document.getElementById('sectionInput');

    if (branchSelect && sectionContainer && sectionInput) {
        const updateSection = () => {
            const branch = branchSelect.value;
            const currentVal = sectionInput.value;

            const newSelect = document.createElement('select');
            newSelect.id = 'sectionInput';
            newSelect.name = 'section';
            newSelect.className = 'notebook-input form-select';

            if (branch === 'CSE' || branch === 'CSE (AIML)' || branch === 'CSE (DS)') {
                for (let i = 11; i <= 28; i++) {
                    const opt = document.createElement('option');
                    opt.value = i;
                    opt.textContent = i;
                    newSelect.appendChild(opt);
                }
            } else {
                ['A', 'B', 'C'].forEach(letter => {
                    const opt = document.createElement('option');
                    opt.value = letter;
                    opt.textContent = letter;
                    newSelect.appendChild(opt);
                });
            }

            if (currentVal) {
                const optionExists = Array.from(newSelect.options).some(opt => opt.value === currentVal);
                if (optionExists) {
                    newSelect.value = currentVal;
                }
            }

            sectionContainer.replaceChild(newSelect, sectionInput);
            sectionInput = newSelect;
        };

        branchSelect.addEventListener('change', updateSection);
        updateSection();
    }

    // ===== PROFILE IMAGE PREVIEW (simple, no crop) =====
    const profileInput = document.getElementById('profile_image');
    const profilePreview = document.getElementById('profilePreview');
    if (profileInput && profilePreview) {
        profileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(ev) {
                    profilePreview.src = ev.target.result;
                };
                reader.readAsDataURL(file);
            } else {
                profilePreview.src = window.DEFAULT_PROFILE_IMAGE;  // fallback
            }
        });
    }

    // ===== SKILLS HANDLING (checkboxes) =====
    const isWorkerCheckbox = document.getElementById('isWorker');
    const skillsSection = document.querySelector('.skills-section');
    const skillCheckboxes = document.querySelectorAll('.skill-checkbox');
    const skillsHidden = document.getElementById('skillsHidden');

    function updateSkillsHidden() {
        const selected = [];
        skillCheckboxes.forEach(cb => {
            if (cb.checked) selected.push(cb.value);
        });
        skillsHidden.value = selected.join(', ');
    }

    if (isWorkerCheckbox && skillsSection) {
        function toggleSkills() {
            if (isWorkerCheckbox.checked) {
                skillsSection.style.display = 'block';
            } else {
                skillsSection.style.display = 'none';
                // Uncheck all when hidden
                skillCheckboxes.forEach(cb => cb.checked = false);
                updateSkillsHidden();
            }
        }
        isWorkerCheckbox.addEventListener('change', toggleSkills);
        toggleSkills(); // initial state
    }

    skillCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateSkillsHidden);
    });

    // If editing, pre-populate checkboxes from existing skills
    if (skillsHidden && skillsHidden.value) {
        const existing = skillsHidden.value.split(',').map(s => s.trim()).filter(s => s);
        skillCheckboxes.forEach(cb => {
            if (existing.includes(cb.value)) {
                cb.checked = true;
            }
        });
    }

    // On form submit, ensure skillsHidden is updated
    const form = document.getElementById('signupForm') || document.getElementById('editProfileForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            updateSkillsHidden(); // final update before submit
            if (!isWorkerCheckbox.checked) {
                skillsHidden.value = ''; // clear if not worker
            }
        });
    }

    // ===== LIVE USERNAME/EMAIL CHECK =====
    const usernameInput = document.querySelector('input[name="username"]');
    const emailInput = document.querySelector('input[name="email"]');

    function checkAvailability(field, value, feedbackElement) {
        if (!value) return;
        fetch(`/auth/check-availability?field=${field}&value=${encodeURIComponent(value)}`)
            .then(res => res.json())
            .then(data => {
                feedbackElement.textContent = data.message;
                feedbackElement.style.color = data.available ? 'green' : 'red';
            })
            .catch(err => console.error('Availability check failed:', err));
    }

    if (usernameInput) {
        const feedback = document.createElement('small');
        feedback.className = 'form-text';
        usernameInput.parentNode.appendChild(feedback);
        usernameInput.addEventListener('blur', () => {
            checkAvailability('username', usernameInput.value, feedback);
        });
    }

    if (emailInput) {
        const feedback = document.createElement('small');
        feedback.className = 'form-text';
        emailInput.parentNode.appendChild(feedback);
        emailInput.addEventListener('blur', () => {
            checkAvailability('email', emailInput.value, feedback);
        });
    }
});