// script.js
document.addEventListener("DOMContentLoaded", function() {
    const lastUpdatedElement = document.getElementById('last-updated');
    const lastUpdatedDate = new Date(document.lastModified);
    lastUpdatedElement.textContent = lastUpdatedDate.toLocaleDateString('en-GB');
});
