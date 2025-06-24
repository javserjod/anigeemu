document.addEventListener("DOMContentLoaded", () => {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');


    const image = document.getElementById("image-original");
    
    if (image) {
        if (image.complete) {
            image.classList.add("visible");
        } else {
            image.addEventListener("load", function () {
                image.classList.add("visible");
            });
        }
    }

    const sentDataContainer = document.getElementById("round-answer-data-container");
    
    if (sentDataContainer){
        
        const correctAnswerId = sentDataContainer.dataset.roundDbId;
        const gamemode = sentDataContainer.dataset.gameMode;

        // Container for fetched data. Just visual effect for loading
        const fetchedDataContainer = sentDataContainer.querySelector("#fetched-data-container");
        fetchedDataContainer.classList.remove("visible"); 
        fetchedDataContainer.classList.add("fade-in");

        console.log("Answer ID in Anilist:", correctAnswerId);
        
        if (gamemode === "Cover Image") {
            fetchAnswerMedia(correctAnswerId)
            .then(data => {
                renderAnswerMedia(data)})
            .catch(error => {
                console.error("Error fetching media data:", error);
                const container = document.getElementById("round-details-container");
                container.innerHTML = `
                    <div class="alert alert-danger" role="alert">; 
                        Failed to fetch media data. Please try again later.
                    </div>
                `;
            })

        } else if (gamemode === "Character Image") {
            fetchAnswerCharacter(correctAnswerId)
            .then(data => {
                renderAnswerCharacter(data)})
            .catch(error => {
                console.error("Error fetching character data:", error);
                const container = document.getElementById("round-details-container");
                container.innerHTML = `
                    <div class="alert alert-danger" role="alert">;
                        Failed to fetch character data. Please try again later.
                    </div>
                `;
            })
        }

        async function fetchAnswerMedia(correctAnswerId) {

            try {
                const res = await fetch("/get_anilist_data/", {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({ 
                        type: "Media",
                        id: correctAnswerId,
                    })
                });

                const data = await res.json();
                return data;
            } catch (error) {
                console.error("Error fetching media answer additional info:", error);
            }
        }
                
        function renderAnswerMedia(data) {
            const media = data.data.Media

            if (media.title.english != null && media.title.english !== media.title.romaji) {
                document.getElementById("other-name").textContent = media.title.english;
            }
            
            const desc = media.description.replace(/(<br\s*\/?>\s*){3,}/gi, '<br><br>') || "No description available.";  // Replace multiple <br> with two <br>
            const genreList = media.genres?.join(", ") || null;
            const eps = media.episodes;
            const vols = media.volumes;
            const score = media.averageScore;
            const year = media.seasonYear;
            const format = media.format;
            const favourites = media.favourites;
            const popularity = media.popularity;
            const siteUrl = media.siteUrl;
            
            // <li> only if available
            const descItem = desc ? `<li class="list-group-item mb-0 "><strong>Description:</strong> ${desc}</li>` : "No description available.";
            const genreItem = genreList ? `<li class="list-group-item"><strong>Genres:</strong> ${genreList}</li>` : "";
            const epsItem = eps != null ? `<li class="list-group-item"><strong>Episodes:</strong> ${eps}</li>` : "";
            const volsItem = vols != null ? `<li class="list-group-item"><strong>Volumes:</strong> ${vols}</li>` : "";
            const scoreItem = score != null ? `<li class="list-group-item"><strong>Average Score:</strong> ${score}/100</li>` : "";
            const yearItem = year != null ? `<li class="list-group-item"><strong>Year:</strong> ${year}</li>` : "";
            const formatItem = format ? `<li class="list-group-item"><strong>Format:</strong> ${format}</li>` : "";
            const favouritesItem = favourites != null ? `<li class="list-group-item"><strong>Favourites:</strong> ${favourites}</li>` : "";
            const popularityItem = popularity != null ? `<li class="list-group-item"><strong>Popularity:</strong> ${popularity}</li>` : "";

            // HTML
            const html = `
                <div class="card my-4 shadow-sm" style="max-width: 700px; margin: 0 auto;">
                    <a href="${siteUrl}" target="_blank" class="text-white text-decoration-none">
                        <div class="card-header bg-secondary text-white">
                            <h5 class="mb-0">Additional info <i class="bi bi-box-arrow-up-right px-1"></i> </h5>  
                        </div>
                    </a>
                    <div class="card-body pb-0">
                        <ul class="list-group list-group-flush mb-3">
                            ${descItem}
                            ${yearItem}
                            ${genreItem}
                            ${scoreItem}
                            ${formatItem}
                            ${epsItem}
                            ${volsItem}
                            ${favouritesItem}
                            ${popularityItem}
                        </ul>
                    </div>
                </div>
            `;

            const container = document.getElementById("round-details-container");
            container.innerHTML = html;

            requestAnimationFrame(() => {
                fetchedDataContainer.classList.add("visible");
            });

            //console.log("Fetched media data:", media);
        } 

        
        async function fetchAnswerCharacter(correctAnswerId) {

            try {
                const res = await fetch("/get_anilist_data/", {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken  
                    },
                    body: JSON.stringify({ 
                        type: "Character",
                        id: correctAnswerId,
                    })
                });
                
                const data = await res.json();
                return data;
            } catch (error) {
                console.error("Error fetching character answer additional info:", error);
            }
        }
                
        function renderAnswerCharacter(data) {
            const character = data.data.Character
            const mediaEdges = character.media.edges;

            if (character.name.alternative != null && character.name.alternative !== character.name.full) {
                if (character.name.alternative.length > 0) {
                    const firstThree = character.name.alternative.slice(0, 3);  // get to 3
                    document.getElementById("other-name").textContent = firstThree.join(", ");
                }
                document.getElementById("other-name").textContent = character.name.alternative.join(", ");
            }
            //console.log("Character data:", character);
            
            const desc = character.description.replace(/(<br\s*\/?>\s*){3,}/gi, '<br><br>') || "No description available.";  // Replace multiple <br> with two <br>
            const favourites = character.favourites;
            const gender = character.gender;
            const age = character.age;
            const siteUrl = character.siteUrl;

            // <li> only if available
            const descItem = desc ? `<li class="list-group-item mb-0"> ${desc}</li>` : "No description available.";
            const favouritesItem = favourites != null ? `<li class="list-group-item"><strong>Favourites:</strong> ${favourites}</li>` : "";
            const genderItem = gender ? `<li class="list-group-item"><strong>Gender:</strong> ${gender}</li>` : "";
            const ageItem = age ? `<li class="list-group-item"><strong>Age:</strong> ${age}</li>` : "";

            // HTML
            const html = `
                <div class="card my-4 shadow-sm" style="max-width: 700px; margin: 0 auto;">
                    <a href="${siteUrl}" target="_blank" class="text-white text-decoration-none">
                        <div class="card-header bg-secondary text-white">
                            <h5 class="mb-0">Additional info <i class="bi bi-box-arrow-up-right px-1"></i> </h5>  
                        </div>
                    </a>
                    <div class="card-body pb-0">
                        <ul class="list-group list-group-flush mb-3">
                            ${descItem}
                            ${genderItem}
                            ${ageItem}
                            ${favouritesItem}
                        </ul>
                        
                    </div>
                </div>
            `;

            
            const infoContainer = document.getElementById("round-details-container");
            infoContainer.innerHTML = html;   // add HTML to the container

            // spoiler hiding and showing functionality
            document.querySelectorAll('#round-details-container span.markdown_spoiler').forEach(spoiler => {
                spoiler.addEventListener('click', () => {
                    spoiler.classList.toggle('markdown_spoiler');
                });
                
                // open links in new tab
                spoiler.querySelectorAll('a').forEach(link => {
                    link.setAttribute('target', '_blank');
                })
            });


            // Character roles
            const characterParticipationsContainer = document.getElementById("character-participations");

            mediaEdges.forEach(edge => {
                const titleRomaji = edge.node.title.romaji;
                const titleEnglish = edge.node.title.english;
                const role = edge.characterRole;
                const format = edge.node.format;
                const cover = edge.node.coverImage.large;
                const seasonYear = edge.node.seasonYear ? edge.node.seasonYear : "Unknown Year";
                const siteUrl = edge.node.siteUrl;

                const mediaItem = document.createElement("div");
                mediaItem.className = "card mb-3 d-flex flex-column";
                mediaItem.style.maxWidth = "200px";
                mediaItem.innerHTML = `
                <a href="${siteUrl}" target="_blank" class="stretched-link text-decoration-none text-dark d-flex flex-column h-100">
                    <img src="${cover}" alt="${titleRomaji}" class="card-img-top mx-auto mb-1 d-block" style="width: 100%; height: 300px; object-fit: fill;"> 
                    
                    <div class="card-body d-flex flex-column justify-content-between p-2" style="flex: 1;">
                        <h6 class="card-title mb-1 p-0">${titleRomaji} ${titleEnglish ? `(<em>${titleEnglish}</em>)` : ""}</h6>
                        <div class="mt-auto">
                            <hr>
                            <small class="text-muted d-block">${format}, ${seasonYear}</small>
                            <small class="text-muted d-block">${role}</small> 
                        </div>
                    </div>
                </a>
                `;
                characterParticipationsContainer.appendChild(mediaItem);  
            })

            requestAnimationFrame(() => {
                fetchedDataContainer.classList.add("visible");
            });

            //console.log("Fetched media data:", media);
        } 
    }
});