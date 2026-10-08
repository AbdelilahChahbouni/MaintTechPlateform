/**
 * Dynamic Talent Search Engine for MaintTech Jobs Maroc
 * Uses modern Fetch API for instant, live client-side filtering without page reloads.
 */

document.addEventListener('DOMContentLoaded', () => {
    const talentsGrid = document.getElementById('talents-grid');
    const talentCount = document.getElementById('talent-count');
    const loadingIndicator = document.getElementById('talents-loading');
    const emptyState = document.getElementById('talents-empty-state');

    // Filter Elements
    const searchInput = document.getElementById('filter-search');
    const citySelect = document.getElementById('filter-city');
    const specialtySelect = document.getElementById('filter-specialty');
    const expSelect = document.getElementById('filter-experience');
    const mobilityCheck = document.getElementById('filter-mobility');
    const resetBtn = document.getElementById('btn-reset-filters');

    if (!talentsGrid) return;

    let debounceTimer = null;

    /**
     * Escape HTML helper to prevent XSS
     */
    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Fetch talents from Flask JSON API with active filter parameters
     */
    async function fetchTalents() {
        if (loadingIndicator) loadingIndicator.classList.remove('hidden');
        if (emptyState) emptyState.classList.add('hidden');

        const params = new URLSearchParams();

        if (searchInput && searchInput.value.trim()) {
            params.append('search', searchInput.value.trim());
        }
        if (citySelect && citySelect.value && citySelect.value !== 'all') {
            params.append('city', citySelect.value);
        }
        if (specialtySelect && specialtySelect.value && specialtySelect.value !== 'all') {
            params.append('specialty', specialtySelect.value);
        }
        if (expSelect && expSelect.value && expSelect.value !== 'all') {
            params.append('min_exp', expSelect.value);
        }
        if (mobilityCheck && mobilityCheck.checked) {
            params.append('mobility', 'true');
        }

        try {
            const response = await fetch(`/api/talents?${params.toString()}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (data.success) {
                renderTalents(data.talents, data.is_recruiter);
                if (talentCount) {
                    talentCount.textContent = data.count;
                }
            }
        } catch (error) {
            console.error('Erreur lors du chargement des techniciens:', error);
            talentsGrid.innerHTML = `
                <div class="col-span-full py-12 text-center text-red-500">
                    <i class="fa-solid fa-triangle-exclamation text-3xl mb-3"></i>
                    <p class="font-medium">Une erreur est survenue lors de la récupération des profils.</p>
                </div>
            `;
        } finally {
            if (loadingIndicator) loadingIndicator.classList.add('hidden');
        }
    }

    /**
     * Render talent cards dynamically in the grid
     */
    function renderTalents(talents, isRecruiter) {
        if (!talents || talents.length === 0) {
            talentsGrid.innerHTML = '';
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');

        const cardsHtml = talents.map(talent => {
            const skillsHtml = (talent.skills || []).slice(0, 4).map(skill => `
                <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200">
                    <i class="fa-solid fa-microchip text-[10px] text-blue-500 mr-1.5"></i>
                    ${escapeHtml(skill)}
                </span>
            `).join('');

            const extraSkillsCount = Math.max(0, (talent.skills || []).length - 4);
            const extraBadge = extraSkillsCount > 0 
                ? `<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold bg-blue-50 text-blue-700">+${extraSkillsCount}</span>` 
                : '';

            const mobilityBadge = talent.mobility
                ? `<span class="inline-flex items-center text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                     <i class="fa-solid fa-check text-[10px] mr-1"></i> Mobile
                   </span>`
                : `<span class="inline-flex items-center text-xs font-medium text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full">
                     <i class="fa-solid fa-location-pin text-[10px] mr-1"></i> Fixe
                   </span>`;

            const cvBadge = talent.cv_available
                ? `<span class="inline-flex items-center text-xs font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                     <i class="fa-solid fa-file-pdf mr-1 text-red-500"></i> CV Disponible
                   </span>`
                : '';

            const displayName = isRecruiter ? talent.full_name : talent.anonymous_name;
            const avatarHtml = talent.photo_filename
                ? `<img src="/uploads/avatars/${escapeHtml(talent.photo_filename)}" alt="${escapeHtml(displayName)}" class="w-12 h-12 rounded-xl object-cover shadow-sm border border-slate-200">`
                : `<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-slate-900 to-blue-900 text-white flex items-center justify-center font-bold text-lg shadow-sm">
                     ${escapeHtml(displayName.substring(0, 2).toUpperCase())}
                   </div>`;

            const contactLockNotice = !isRecruiter 
                ? `<span class="text-[11px] text-slate-500 flex items-center" title="Connectez-vous en tant que recruteur pour voir les coordonnées directes">
                     <i class="fa-solid fa-lock text-[10px] mr-1 text-amber-500"></i> Contact masqué
                   </span>` 
                : `<span class="text-[11px] text-emerald-600 font-medium flex items-center">
                     <i class="fa-solid fa-phone text-[10px] mr-1"></i> Direct RH
                   </span>`;

            return `
                <div class="talent-card bg-white rounded-xl border border-slate-200/90 shadow-sm p-6 flex flex-col justify-between hover:border-blue-400 transition-all duration-200">
                    <div>
                        <!-- Header: Avatar & Info -->
                        <div class="flex items-start justify-between gap-4 mb-4">
                            <div class="flex items-center gap-3">
                                ${avatarHtml}
                                <div>
                                    <div class="flex items-center gap-2">
                                        <h3 class="font-bold text-slate-900 text-base leading-tight">${escapeHtml(displayName)}</h3>
                                    </div>
                                    <p class="text-xs font-semibold text-blue-600 uppercase tracking-wider mt-0.5">${escapeHtml(talent.specialty)}</p>
                                </div>
                            </div>
                            <div class="text-right">
                                ${contactLockNotice}
                            </div>
                        </div>

                        <!-- Meta badges (City, Exp, Mobility) -->
                        <div class="flex flex-wrap items-center gap-2 text-xs text-slate-600 mb-4 pb-3 border-b border-slate-100">
                            <span class="inline-flex items-center font-medium text-slate-700">
                                <i class="fa-solid fa-location-dot text-red-500 mr-1.5"></i> ${escapeHtml(talent.city)}
                            </span>
                            <span class="text-slate-300">•</span>
                            <span class="inline-flex items-center font-medium text-slate-700">
                                <i class="fa-solid fa-briefcase text-slate-400 mr-1.5"></i> ${talent.experience_years} ans d'exp.
                            </span>
                            <span class="text-slate-300">•</span>
                            ${mobilityBadge}
                        </div>

                        <!-- Bio Snippet -->
                        <p class="text-slate-600 text-xs line-clamp-2 mb-4 leading-relaxed">
                            ${escapeHtml(talent.bio || "Technicien de maintenance industrielle qualifié et disponible.")}
                        </p>

                        <!-- Key Skills Tags -->
                        <div class="mb-5">
                            <p class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Compétences Techniques</p>
                            <div class="flex flex-wrap gap-1.5">
                                ${skillsHtml}
                                ${extraBadge}
                            </div>
                        </div>
                    </div>

                    <!-- Footer Actions -->
                    <div class="pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
                        ${cvBadge}
                        <a href="/talents/${talent.id}" class="ml-auto inline-flex items-center justify-center px-4 py-2 bg-slate-900 hover:bg-blue-600 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors duration-150">
                            <span>Voir le Profil</span>
                            <i class="fa-solid fa-arrow-right ml-1.5 text-[11px]"></i>
                        </a>
                    </div>
                </div>
            `;
        }).join('');

        talentsGrid.innerHTML = cardsHtml;
    }

    // -----------------------------------------------------------------
    // Event Listeners with Debounce for search
    // -----------------------------------------------------------------
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                fetchTalents();
            }, 300);
        });
    }

    if (citySelect) citySelect.addEventListener('change', fetchTalents);
    if (specialtySelect) specialtySelect.addEventListener('change', fetchTalents);
    if (expSelect) expSelect.addEventListener('change', fetchTalents);
    if (mobilityCheck) mobilityCheck.addEventListener('change', fetchTalents);

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            if (citySelect) citySelect.value = 'all';
            if (specialtySelect) specialtySelect.value = 'all';
            if (expSelect) expSelect.value = 'all';
            if (mobilityCheck) mobilityCheck.checked = false;
            fetchTalents();
        });
    }

    // Initialize from URL parameters if present (e.g. from homepage search bar)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('search') && searchInput) {
        searchInput.value = urlParams.get('search');
    }
    if (urlParams.has('city') && citySelect) {
        citySelect.value = urlParams.get('city');
    }
    if (urlParams.has('specialty') && specialtySelect) {
        specialtySelect.value = urlParams.get('specialty');
    }

    // Initial API load if parameters were set, or trigger immediate sync
    if (urlParams.toString()) {
        fetchTalents();
    }
});
