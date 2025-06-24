document.addEventListener('DOMContentLoaded', () => {
    
    const imgAlternateContainer = document.getElementById('image-alternate-container');

    const imgToGuessContainer = document.getElementById('image-to-guess-container');
    
    if (imgAlternateContainer) {
        imgAlternateContainer.scrollIntoView({
            behavior: 'auto',
            block: 'center',
            inline: 'nearest' 
        });
    }else if (imgToGuessContainer) {
        imgToGuessContainer.scrollIntoView({
            behavior: 'auto',
            block: 'center',
            inline: 'nearest'
        });
    }

});