document.addEventListener('DOMContentLoaded', () => {
    
    // Source selection cards
    const sourceCards = document.querySelectorAll('#sourceCards .option-card');
    const hiddenInputGameSource = document.getElementById('game-source-hidden');

    sourceCards.forEach(card => {
    card.addEventListener('click', () => {
        sourceCards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        hiddenInputGameSource.value = card.getAttribute('data-value');
    });
    });


    // Game Mode selection cards
    const modeCards = document.querySelectorAll('#gameModeCards .option-card');
    const hiddenInputGameMode = document.getElementById('game-mode-hidden');

    modeCards.forEach(card => {
    card.addEventListener('click', () => {
        modeCards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        hiddenInputGameMode.value = card.getAttribute('data-value');
    });
    });


    // Genres selection cards (fetch all genres from the server)
    async function fetchGenres() {
        const query = `query { GenreCollection }`;

        const response = await fetch("https://graphql.anilist.co", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
        });

        const result = await response.json();
        return result.data.GenreCollection;
    }

    function filterGenres(genres) {
        // remove adult genres
        return genres.filter(genre => genre !== "Hentai");
    }

    
    function renderGenres(genres) {
        const container = document.getElementById("genreCards");
        const controlContainer = document.getElementById("genreControls");
        const hiddenInputGenres = document.getElementById("game-genres-hidden");
        const loadingSpinner = document.getElementById("loadingSpinner");
        let selected = new Set();
        
        function triggerClickEffect(card) {
            card.classList.add("clicked");
            setTimeout(() => card.classList.remove("clicked"), 400);
        }

        // hide spinner
        loadingSpinner.style.display = "none";
        
        const updateHiddenInputGenres = () => {
            hiddenInputGenres.value = Array.from(selected).join(",");
        };

        // select all genres card
        const selectAllCard = document.createElement("div");
        selectAllCard.className = "control-card";
        selectAllCard.textContent = "Select All";

        selectAllCard.addEventListener("click", () => {
            const genreCards = document.querySelectorAll(".genre-card");
            genreCards.forEach(card => {
                card.classList.add("selected");
                selected.add(card.dataset.value);
            });
            updateHiddenInputGenres();
            triggerClickEffect(selectAllCard);
        });
        controlContainer.appendChild(selectAllCard);

        // deselect all genres card
        const unselectAllCard = document.createElement("div");
        unselectAllCard.className = "control-card";
        unselectAllCard.textContent = "Unselect All";
        unselectAllCard.addEventListener("click", () => {
            const genreCards = document.querySelectorAll(".genre-card");
            genreCards.forEach(card => {
                card.classList.remove("selected");
            });
            selected.clear();
            updateHiddenInputGenres();
            triggerClickEffect(unselectAllCard);
        });
        controlContainer.appendChild(unselectAllCard);


        // show cards fetched from the server
        genres.forEach((genre) => {
            const card = document.createElement("div");
            card.className = "option-card genre-card selected";  // selected by default
            card.textContent = genre;
            card.dataset.value = genre;

            card.addEventListener("click", () => {

                card.classList.toggle("selected");
                if (selected.has(genre)) {
                selected.delete(genre);
                } else {
                selected.add(genre);
                }
                hiddenInputGenres.value = Array.from(selected).join(",");
            });

            container.appendChild(card);
        });
        
    }

    // Check if the hidden input for genres exists and fetch genres (meaning we are on the correct page)
    if (document.getElementById("game-genres-hidden")) {
        fetchGenres()
        /* update hidden input with all genres by default */
        .then(genres => {
            genres = filterGenres(genres);
            const hiddenInputGenres = document.getElementById("game-genres-hidden");
            hiddenInputGenres.value = genres.join(",");
            return genres;
        })
        .then(renderGenres)
        .catch(() => {
            document.getElementById("loadingSpinner").innerHTML = '<div class="alert alert-danger" role="alert">Failed to load genres. Please try again later.</div>';
        });
    }

    // at least one genre must be selected (with class "selected")
    if (document.getElementById("submitConfigButton")) {
        document.getElementById("submitConfigButton").addEventListener("click", (event) => {
            const genreCardsSelected = document.querySelectorAll(".genre-card.selected");

            if (genreCardsSelected.length === 0) {
                event.preventDefault();
                alert("Please select at least one genre.");
                return;
            }
        });
    }

});
