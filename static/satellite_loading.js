// Satellite Loading Animation Script

function createSatelliteLoader(container, message = "Loading satellite data...") {
  // Create CSS link if it doesn't exist
  if (!document.getElementById('satellite-loader-css')) {
    const link = document.createElement('link');
    link.id = 'satellite-loader-css';
    link.rel = 'stylesheet';
    link.href = 'static/satellite_loading.css';
    document.head.appendChild(link);
  }
  
  // Create the loader HTML
  const loaderHTML = `
    <div class="satellite-loader">
      <div class="earth"></div>
      <div class="orbit">
        <div class="satellite"></div>
      </div>
      <div class="satellite-pulse"></div>
    </div>
    <div class="loading-text">${message}</div>
  `;
  
  // Set the HTML content of the container
  container.innerHTML = loaderHTML;
  
  // Return a function to remove the loader
  return function removeLoader() {
    container.innerHTML = '';
  };
}

// Add to window object so it can be accessed from Streamlit components
window.createSatelliteLoader = createSatelliteLoader;