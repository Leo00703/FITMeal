// Main scripts for FitMeal Planner
console.log('FitMeal Planner loaded');
document.addEventListener('DOMContentLoaded', function() {
    
    // --- Base Layout Logic ---
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            document.querySelector('.nav-links').classList.toggle('active');
        });
    }

    // --- Profile Page Logic ---
    const logoutLink = document.querySelector('.logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    }

    // --- Planner Form Logic ---
    if (document.getElementById('plannerForm')) {
        // Initialize selected cards
        const checkedInputs = document.querySelectorAll('.selection-card input:checked');
        checkedInputs.forEach(input => {
            input.closest('.selection-card').classList.add('selected');
        });

        // Tag System Logic
        const tagInput = document.getElementById('tagInput');
        const tagContainer = document.getElementById('tagContainer');
        const hiddenInput = document.getElementById('allergiesHidden');
        const suggestionsDropdown = document.getElementById('suggestionsDropdown');
        
        let tags = [];
        const suggestions = [
            "Peanuts", "Tree Nuts", "Milk", "Egg", "Wheat", "Soy", "Fish", "Shellfish", 
            "Gluten", "Dairy", "Sesame", "Mustard", "Celery", "Lupin", "Sulfites",
            "Mushrooms", "Tomatoes", "Avocado", "Bananas", "Strawberries"
        ];

        function renderTags() {
            // Clear existing tags (except input)
            const existingTags = tagContainer.querySelectorAll('.tag-pill');
            existingTags.forEach(tag => tag.remove());
            
            // Add tags
            tags.forEach(tag => {
                const pill = document.createElement('div');
                pill.className = 'tag-pill';
                pill.innerHTML = `
                    ${tag}
                    <span class="tag-remove" data-tag="${tag}">&times;</span>
                `;
                tagContainer.insertBefore(pill, tagInput);
            });
            
            // Update hidden input
            hiddenInput.value = tags.join(', ');

            // Re-attach listeners to new remove buttons
            document.querySelectorAll('.tag-remove').forEach(btn => {
                btn.addEventListener('click', function() {
                    removeTag(this.getAttribute('data-tag'));
                });
            });
        }

        function addTag(tag) {
            tag = tag.trim();
            if (tag && !tags.includes(tag)) {
                tags.push(tag);
                renderTags();
            }
            tagInput.value = '';
            suggestionsDropdown.style.display = 'none';
        }

        function removeTag(tag) {
            tags = tags.filter(t => t !== tag);
            renderTags();
        };

        // Expose addTag and removeTag to window for inline onclicks
        window.addTag = addTag;
        window.removeTag = removeTag;

        // Input Event Listeners
        tagInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addTag(this.value);
            } else if (e.key === 'Backspace' && this.value === '' && tags.length > 0) {
                removeTag(tags[tags.length - 1]);
            }
        });

        tagInput.addEventListener('input', function() {
            const value = this.value.toLowerCase();
            if (value.length > 0) {
                const filtered = suggestions.filter(s => s.toLowerCase().includes(value) && !tags.includes(s));
                if (filtered.length > 0) {
                    suggestionsDropdown.innerHTML = filtered.map(s => 
                        `<div class="suggestion-item" onclick="addTag('${s}')">${s}</div>`
                    ).join('');
                    suggestionsDropdown.style.display = 'block';
                } else {
                    suggestionsDropdown.style.display = 'none';
                }
            } else {
                suggestionsDropdown.style.display = 'none';
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!tagContainer.contains(e.target)) {
                suggestionsDropdown.style.display = 'none';
            }
        });

        // Form Submit Loading
        document.getElementById('plannerForm').addEventListener('submit', function(e) {
            // Validation
            const goal = document.querySelector('input[name="goal"]:checked');
            const meals = document.querySelector('input[name="meals_per_day"]:checked');
            const diet = document.querySelector('input[name="diet"]:checked');
            
            if (!goal || !meals || !diet) {
                e.preventDefault();
                alert('Please select all required options (Goal, Meals per Day, and Diet Type) before generating your plan.');
                return;
            }

            document.getElementById('loadingOverlay').style.display = 'flex';
        });
    }

    // --- Plan Page Logic ---
    if (document.querySelector('.day-card')) {
        // Carousel Logic
        let currentIndex = 0;
        const itemsPerPage = 3;
        const dayCards = document.querySelectorAll('.day-card');
        const totalItems = dayCards.length;
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        function updateCarousel() {
            // Determine items per page based on screen width
            let visibleCount = itemsPerPage;
            if (window.innerWidth <= 768) visibleCount = 1;
            else if (window.innerWidth <= 992) visibleCount = 2;

            // Hide all
            dayCards.forEach(card => card.classList.remove('active'));

            // Show current slice
            for (let i = 0; i < visibleCount; i++) {
                if (currentIndex + i < totalItems) {
                    dayCards[currentIndex + i].classList.add('active');
                }
            }

            // Update buttons
            if (prevBtn && nextBtn) {
                prevBtn.disabled = currentIndex === 0;
                nextBtn.disabled = currentIndex + visibleCount >= totalItems;
            }
        }

        function moveCarousel(direction) {
            let visibleCount = itemsPerPage;
            if (window.innerWidth <= 768) visibleCount = 1;
            else if (window.innerWidth <= 992) visibleCount = 2;

            const newIndex = currentIndex + direction;
            
            if (newIndex >= 0 && newIndex <= totalItems - visibleCount) {
                currentIndex = newIndex;
                updateCarousel();
            }
        }
        
        // Expose moveCarousel
        window.moveCarousel = moveCarousel;

        // Initial call
        updateCarousel();
        
        // Update on resize
        window.addEventListener('resize', () => {
            currentIndex = 0; // Reset to start on resize to avoid index issues
            updateCarousel();
        });

        // Save Plan Logic
        const saveBtn = document.getElementById('savePlanBtn');
        if (saveBtn) {
            // Initialize button state
            // planStatus is defined in the HTML
            if (typeof window.planStatus !== 'undefined') {
                updateSaveButton(window.planStatus);
            }
        }
    }
    
    // Modal backdrop click
    const mealModal = document.getElementById('mealModal');
    if (mealModal) {
        mealModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    }
});

// Global functions (needed for onclick attributes)

// Planner Form
function selectCard(card, groupName) {
    // Remove selected class from all cards in this group
    const cards = document.querySelectorAll(`.selection-card input[name="${groupName}"]`);
    cards.forEach(input => {
        input.closest('.selection-card').classList.remove('selected');
    });
    
    // Add selected class to clicked card
    card.classList.add('selected');
    
    // Check the radio button (handled by label click usually, but ensuring here)
    const radio = card.querySelector('input[type="radio"]');
    if (radio) radio.checked = true;
}

// Plan Page
function openMealModal(meal) {
    const modal = document.getElementById('mealModal');
    const body = document.getElementById('modalBody');
    
    // Default values if data is missing (for older plans)
    const calories = meal.calories || 'N/A';
    const protein = meal.macros ? meal.macros.protein : 'N/A';
    const carbs = meal.macros ? meal.macros.carbs : 'N/A';
    const fat = meal.macros ? meal.macros.fat : 'N/A';
    const ingredients = meal.ingredients || ['Ingredients not available for this plan.'];
    const instructions = meal.instructions || ['Instructions not available for this plan.'];

    let ingredientsHtml = '<ul class="ingredient-list">';
    ingredients.forEach(ing => {
        ingredientsHtml += `<li class="ingredient-item">${ing}</li>`;
    });
    ingredientsHtml += '</ul>';

    let instructionsHtml = '<div>';
    instructions.forEach((step, index) => {
        instructionsHtml += `
            <div class="instruction-step">
                <div class="step-number">${index + 1}</div>
                <div>${step}</div>
            </div>
        `;
    });
    instructionsHtml += '</div>';

    // Determine meal tag colors
    let mealTagBg = '#edf2f7';
    let mealTagColor = '#4a5568';
    const mealType = meal.meal || '';
    
    if (mealType.includes('Breakfast')) {
        mealTagBg = '#FEFCBF'; // Light Yellow
        mealTagColor = '#744210';
    } else if (mealType.includes('Lunch')) {
        mealTagBg = '#C6F6D5'; // Light Green
        mealTagColor = '#22543D';
    } else if (mealType.includes('Dinner')) {
        mealTagBg = '#BEE3F8'; // Light Blue
        mealTagColor = '#2A4365';
    } else if (mealType.includes('Snack')) {
        mealTagBg = '#FED7E2'; // Light Pink
        mealTagColor = '#702459';
    }

    // Use window.favoriteIds
    const favoriteIds = window.favoriteIds || [];
    const isFavorite = favoriteIds.includes(meal.id);
    const favBtnText = isFavorite ? 'Added to Favorites' : 'Add to Favorites';
    const favBtnClass = isFavorite ? 'btn-favorite-active' : '';
    const favBtnStyle = isFavorite ? 'background-color: #e53e3e; color: white; border-color: #e53e3e;' : '';

    body.innerHTML = `
        <div class="modal-heart-icon ${isFavorite ? 'visible' : ''}" id="modalHeartIcon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
        </div>
        <div style="text-align: center; margin-bottom: 2rem;">
            <span class="tag" style="font-size: 0.9rem; padding: 4px 12px; margin-bottom: 0.5rem; display: inline-block; background: ${mealTagBg}; color: ${mealTagColor};">${meal.meal}</span>
            <h2 style="font-size: 2rem; margin: 0.5rem 0;">${meal.recipe_name}</h2>
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; background: var(--color-card); padding: 0.5rem 1.2rem; border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.1);">
                <span style="font-size: 1.2rem;">⏱</span>
                <span style="font-weight: 600; color: var(--color-text); font-size: 1.1rem;">${meal.time}</span>
            </div>
        </div>

        <div class="nutrition-grid">
            <div class="nutri-box calories">
                <span class="nutri-icon">🔥</span>
                <span class="nutri-value">${calories}</span>
                <span class="nutri-label">Calories</span>
            </div>
            <div class="nutri-box protein">
                <span class="nutri-icon">🥩</span>
                <span class="nutri-value">${protein}</span>
                <span class="nutri-label">Protein</span>
            </div>
            <div class="nutri-box carbs">
                <span class="nutri-icon">🍞</span>
                <span class="nutri-value">${carbs}</span>
                <span class="nutri-label">Carbs</span>
            </div>
            <div class="nutri-box fat">
                <span class="nutri-icon">🥑</span>
                <span class="nutri-value">${fat}</span>
                <span class="nutri-label">Fat</span>
            </div>
        </div>

        <div class="section-header">🛒 Ingredients</div>
        ${ingredientsHtml}

        <div class="section-header">👨‍🍳 Instructions</div>
        ${instructionsHtml}
        
        <div style="margin-top: 2rem; text-align: center;">
            <button id="favBtn" class="btn btn-outline ${favBtnClass}" style="width: 100%; ${favBtnStyle}" onclick="toggleFavorite('${meal.id}', '${meal.recipe_name.replace(/'/g, "\\'")}')">
                ❤️ ${favBtnText}
            </button>
        </div>
    `;

    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('mealModal');
    if (modal) modal.classList.remove('active');
}

function toggleFavorite(recipeId, recipeName) {
    fetch('/toggle_favorite/' + recipeId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ recipe_name: recipeName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const btn = document.getElementById('favBtn');
            const modalHeart = document.getElementById('modalHeartIcon');
            
            // Update local state
            if (data.action === 'added') {
                if (window.favoriteIds) window.favoriteIds.push(recipeId);
                if (btn) {
                    btn.innerHTML = 'Added to Favorites';
                    btn.style.backgroundColor = '#e53e3e';
                    btn.style.color = 'white';
                    btn.style.borderColor = '#e53e3e';
                }
                if (modalHeart) modalHeart.classList.add('visible');
            } else {
                if (window.favoriteIds) window.favoriteIds = window.favoriteIds.filter(id => id !== recipeId);
                if (btn) {
                    btn.innerHTML = '❤️ Add to Favorites';
                    btn.style.backgroundColor = ''; // Reset to default
                    btn.style.color = '';
                    btn.style.borderColor = '';
                }
                if (modalHeart) modalHeart.classList.remove('visible');
            }
            
            // Update the card in the grid immediately
            const cardHeart = document.querySelector(`.meal-item[data-meal-id="${recipeId}"] .meal-heart-icon`);
            if (cardHeart) {
                if (data.action === 'added') {
                    cardHeart.classList.add('visible');
                } else {
                    cardHeart.classList.remove('visible');
                }
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateSaveButton(status) {
    const saveBtn = document.getElementById('savePlanBtn');
    if (!saveBtn) return;
    
    if (status === 'saved') {
        saveBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Saved
        `;
        saveBtn.classList.remove('btn-filled-green');
        saveBtn.classList.add('btn-outline-green');
    } else {
        saveBtn.classList.add('btn-filled-green');
        saveBtn.classList.remove('btn-outline-green');
    }
}

function savePlan() {
    fetch('/save_plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateSaveButton('saved');
        }
    })
    .catch(error => console.error('Error saving plan:', error));
}