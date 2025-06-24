document.addEventListener('DOMContentLoaded', () => {
    /// Prevent multiple clicks on the "Next new round" button

    const antiSpamButton = document.getElementById("anti-spam-button");
    
    if (antiSpamButton) {
        antiSpamButton.addEventListener("click", () => {
            console.log("Next new round button clicked. Loading new round...");

            antiSpamButton.disabled = true;

            setTimeout(() => {
                antiSpamButton.disabled = false;
            }, 5000); // Re-enable after 5 seconds

        });
    }
})