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
            // Create new select element
            const newSelect = document.createElement('select');
            newSelect.id = 'sectionInput';
            newSelect.name = 'section';
            newSelect.className = 'notebook-input form-select';

            if (branch === 'CSE') {
                // Options 11 to 28
                for (let i = 11; i <= 28; i++) {
                    const opt = document.createElement('option');
                    opt.value = i;
                    opt.textContent = i;
                    newSelect.appendChild(opt);
                }
            } else {
                // Options A, B, C, D
                ['A', 'B', 'C', 'D'].forEach(letter => {
                    const opt = document.createElement('option');
                    opt.value = letter;
                    opt.textContent = letter;
                    newSelect.appendChild(opt);
                });
            }

            // Replace old input/select with new one
            sectionContainer.replaceChild(newSelect, sectionInput);
            sectionInput = newSelect; // update reference
        };

        branchSelect.addEventListener('change', updateSection);
        // Initial call to set correct dropdown based on current branch
        updateSection();
    }

    // ===== SKILLS HANDLING =====
    const isWorkerCheckbox = document.getElementById('isWorker');
    const skillsSection = document.querySelector('.skills-section');
    const skillsSelect = document.getElementById('skillsSelect');
    const customSkillInput = document.getElementById('customSkill');
    const addCustomBtn = document.getElementById('addCustomSkill');
    const selectedTagsDiv = document.getElementById('selectedSkillsTags');
    const skillsHidden = document.getElementById('skillsHidden');

    // Store selected skills as array
    let selectedSkills = [];

    // Function to update hidden field and tags display
    function updateSkillsHidden() {
        skillsHidden.value = selectedSkills.join(', ');
        // Render tags
        selectedTagsDiv.innerHTML = '';
        selectedSkills.forEach(skill => {
            const span = document.createElement('span');
            span.className = 'notebook-skill-tag me-1 mb-1';
            span.textContent = skill;
            // Add remove button
            const removeBtn = document.createElement('i');
            removeBtn.className = 'fas fa-times ms-2';
            removeBtn.style.cursor = 'pointer';
            removeBtn.addEventListener('click', () => {
                selectedSkills = selectedSkills.filter(s => s !== skill);
                // Also deselect in multi-select if present
                if (skillsSelect) {
                    Array.from(skillsSelect.options).forEach(opt => {
                        if (opt.value === skill) opt.selected = false;
                    });
                }
                updateSkillsHidden();
            });
            span.appendChild(removeBtn);
            selectedTagsDiv.appendChild(span);
        });
    }

    // Toggle skills section based on is_worker
    if (isWorkerCheckbox && skillsSection) {
        function toggleSkills() {
            if (isWorkerCheckbox.checked) {
                skillsSection.style.display = 'block';
            } else {
                skillsSection.style.display = 'none';
                selectedSkills = [];
                updateSkillsHidden();
                // Deselect all in select
                if (skillsSelect) {
                    Array.from(skillsSelect.options).forEach(opt => opt.selected = false);
                }
            }
        }
        isWorkerCheckbox.addEventListener('change', toggleSkills);
        toggleSkills(); // initial state
    }

    // Multi-select change
    if (skillsSelect) {
        skillsSelect.addEventListener('change', function() {
            const selected = Array.from(this.selectedOptions).map(opt => opt.value);
            // Merge with existing, avoid duplicates
            selected.forEach(s => {
                if (!selectedSkills.includes(s)) selectedSkills.push(s);
            });
            updateSkillsHidden();
        });
    }

    // Add custom skill
    if (addCustomBtn && customSkillInput) {
        addCustomBtn.addEventListener('click', function() {
            const custom = customSkillInput.value.trim();
            if (custom && !selectedSkills.includes(custom)) {
                selectedSkills.push(custom);
                updateSkillsHidden();
                customSkillInput.value = '';
            }
        });
        customSkillInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addCustomBtn.click();
            }
        });
    }

    // On edit profile, pre-populate skills from existing data
    if (skillsHidden && skillsHidden.value) {
        const existing = skillsHidden.value.split(',').map(s => s.trim()).filter(s => s);
        selectedSkills = existing;
        // Pre-select in multi-select
        if (skillsSelect) {
            Array.from(skillsSelect.options).forEach(opt => {
                if (existing.includes(opt.value)) opt.selected = true;
            });
        }
        updateSkillsHidden();
    }

    // Before form submit, ensure skillsHidden is populated (should be already)
    const form = document.getElementById('signupForm') || document.getElementById('editProfileForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // If is_worker not checked, clear skillsHidden
            if (!isWorkerCheckbox.checked) {
                skillsHidden.value = '';
            }
        });
    }
});