document.addEventListener('DOMContentLoaded', function() {
    // Confirm before deleting
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this recipe?')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let valid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#dc3545';
                    field.focus();
                } else {
                    field.style.borderColor = '';
                }
            });

            // Special validation for search form
            if (form.classList.contains('search-form')) {
                const searchInput = form.querySelector('input[name="q"]');
                if (searchInput && !searchInput.value.trim()) {
                    valid = false;
                    searchInput.style.borderColor = '#dc3545';
                    searchInput.focus();
                }
            }

            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    });

    // Image preview for forms
    const imageInputs = document.querySelectorAll('input[type="file"][name="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    let preview = input.nextElementSibling;
                    if (!preview || !preview.classList.contains('image-preview')) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview mt-3';
                        input.parentNode.insertBefore(preview, input.nextSibling);
                    }
                    preview.innerHTML = `<img src="${event.target.result}" alt="Preview" style="max-width: 200px; border-radius: 4px;">`;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Dynamic ingredient/instruction fields
    const addIngredientBtn = document.getElementById('add-ingredient');
    const addInstructionBtn = document.getElementById('add-instruction');
    
    if (addIngredientBtn) {
        addIngredientBtn.addEventListener('click', function() {
            const container = document.getElementById('ingredients-container');
            const count = container.children.length + 1;
            const div = document.createElement('div');
            div.className = 'ingredient-row mb-2';
            div.innerHTML = `
                <input type="text" name="ingredients[]" placeholder="Ingredient ${count}" class="form-control" required>
                <button type="button" class="btn btn-danger btn-sm remove-btn" style="margin-top: 0.5rem;">
                    <i class="fas fa-times"></i> Remove
                </button>
            `;
            container.appendChild(div);
            addRemoveListeners();
        });
    }
    
    if (addInstructionBtn) {
        addInstructionBtn.addEventListener('click', function() {
            const container = document.getElementById('instructions-container');
            const count = container.children.length + 1;
            const div = document.createElement('div');
            div.className = 'instruction-row mb-3';
            div.innerHTML = `
                <textarea name="instructions[]" placeholder="Step ${count}" class="form-control" required></textarea>
                <button type="button" class="btn btn-danger btn-sm remove-btn" style="margin-top: 0.5rem;">
                    <i class="fas fa-times"></i> Remove
                </button>
            `;
            container.appendChild(div);
            addRemoveListeners();
        });
    }
    
    function addRemoveListeners() {
        document.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                this.parentElement.remove();
            });
        });
    }
    
    // Initialize any existing remove buttons
    addRemoveListeners();
});