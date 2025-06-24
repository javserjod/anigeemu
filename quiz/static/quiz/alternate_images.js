document.addEventListener('DOMContentLoaded', () => {

    const originalImage = document.getElementById("image-original");
    const modifiedImage = document.getElementById("image-modified");
    const imageAlternateContainer = document.getElementById("image-alternate-container");


    if (imageAlternateContainer){

        // adapt glow border height and width to image
        imageAlternateContainer.style.minHeight = modifiedImage.offsetHeight + "px";
        imageAlternateContainer.style.minWidth = modifiedImage.offsetWidth + "px";

        const roundState = imageAlternateContainer.dataset.roundState;
        
        if (roundState === "CORRECT") {
            imageAlternateContainer.classList.add("glow-correct");
        } else if (roundState === "WRONG") {
            imageAlternateContainer.classList.add("glow-wrong");
        }


        modifiedImage.style.opacity = 0;
        modifiedImage.style.pointerEvents = 'none';

        imageAlternateContainer.addEventListener("click", () => {
            if (originalImage.style.opacity === "1" || originalImage.style.opacity === "") {
                // show modified, hide original
                originalImage.style.opacity = 0;
                originalImage.style.pointerEvents = 'none';
                modifiedImage.style.opacity = 1;
                modifiedImage.style.pointerEvents = 'auto';
            } else {
                // show original, hide modified
                originalImage.style.opacity = 1;
                originalImage.style.pointerEvents = 'auto';
                modifiedImage.style.opacity = 0;
                modifiedImage.style.pointerEvents = 'none';
            }
        });
        
    }
    
});