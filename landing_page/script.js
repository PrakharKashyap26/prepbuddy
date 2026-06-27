document.addEventListener('DOMContentLoaded', () => {
    console.log("PrepBuddy Landing Page Initialized successfully.");
    
    // Add subtle visual effect when features are clicked or hovered
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            // Can be expanded with custom interactions
        });
    });
});
