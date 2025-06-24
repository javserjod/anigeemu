document.addEventListener('DOMContentLoaded', function() {
    

    document.querySelectorAll('.delete-game-button').forEach(deleteButton => {
        deleteButton.addEventListener('click', deleteHandler);
    });

    
});

function deleteHandler(event){
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    event.preventDefault();
    event.stopPropagation();

    const deleteButton = event.currentTarget;
    const gameId = deleteButton.dataset.gameId;
    const cardsContainer = document.querySelector('.card-row');
    const allCols = Array.from(cardsContainer.children);
    const cardToRemove = deleteButton.closest('.record-card');
    const colToRemove = cardToRemove.closest('.card-col');
    const colIndex = allCols.indexOf(colToRemove);

    const currentPage = parseInt(new URLSearchParams(window.location.search).get("page") || "1");

    console.log("Deleted game with ID:", gameId);

    fetch(`/delete_game/${gameId}?page=${currentPage}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error deleting:', data.error);
            return;
        }

        cardToRemove.classList.add('delete-card-effect');

         setTimeout(() => {
            colToRemove.remove();   // remove whole column, containing the card
            
            const remainingCols = Array.from(cardsContainer.children).slice(colIndex);   // columns after the deleted one

            // remove all those later columns
            for (let col of remainingCols) {
                col.remove();
            }
            // and add them back to the end of the list to simulate a move effect
            for (let col of remainingCols) {
                cardsContainer.appendChild(col);
            }

            
            // if card to add from the next page, add it to the end of the list
            if (data.html) {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.html.trim();
                const newCol = tempDiv.firstElementChild;

                cardsContainer.appendChild(newCol);

                const newDeleteBtn = newCol.querySelector('.delete-game-button');
                if (newDeleteBtn) {
                    newDeleteBtn.addEventListener('click', deleteHandler);
                }

            }

        }, 300);
    });
};