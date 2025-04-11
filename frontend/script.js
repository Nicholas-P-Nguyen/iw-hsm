function showScreen(id) {
    const screens = document.querySelectorAll('.container');
    screens.forEach(screen => {
      screen.style.display = 'none';
    });
  
    const target = document.getElementById(id);
    if (target) {
      target.style.display = 'block';
    }
  }
  