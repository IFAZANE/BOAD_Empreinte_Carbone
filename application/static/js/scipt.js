
    function calculateEmission(element) {
      const row = element.closest('tr');
      const select = row.querySelector('select');
      const input = row.querySelector('input[type="number"]');
      const output = row.querySelector('.emission-result');
      const factorCell = row.querySelector('.emission-factor');

      const distance = parseFloat(input.value);
      const factor = parseFloat(select.options[select.selectedIndex].dataset.factor);

      if (!isNaN(factor) && !isNaN(distance)) {
        const emission = factor * distance;
        output.textContent = emission.toFixed(2);
        factorCell.textContent = factor.toFixed(3);
      } else {
        output.textContent = "0.00";
        factorCell.textContent = "-";
      }
    }















const emissionFactors = {
  moto: 0.1,
  voiture: 0.21,
  avion: 0.285,
  bateau: 0.04,
  train: 0.015
};

function calculateEmission(element) {
  const row = element.closest('tr');
  const select = row.querySelector('select');
  const input = row.querySelector('input[type="number"]');
  const output = row.querySelector('.emission-result');
  const factorCell = row.querySelector('.emission-factor');

  const engin = select.value;
  const distance = parseFloat(input.value);

  let emission = 0;
  if (engin && !isNaN(distance)) {
    const factor = emissionFactors[engin] || 0;
    emission = factor * distance;
    output.textContent = emission.toFixed(2);
    factorCell.textContent = factor;
  } else {
    output.textContent = 0;
    factorCell.textContent = '-';
  }

  updateSubtotals();
}

function updateSubtotals() {
  const rows = document.querySelectorAll('tbody tr');
  let subtotalPersonnes = 0;
  let subtotalMarchandises = 0;

  let currentSection = 'personnes';

  rows.forEach(row => {
    if (row.classList.contains('section-title')) {
      const text = row.textContent.toLowerCase();
      if (text.includes('marchandises')) {
        currentSection = 'marchandises';
      } else if (text.includes('personnes')) {
        currentSection = 'personnes';
      }
    }

    const emissionCell = row.querySelector('.emission-result');
    if (emissionCell) {
      const val = parseFloat(emissionCell.textContent) || 0;
      if (currentSection === 'personnes') {
        subtotalPersonnes += val;
      } else {
        subtotalMarchandises += val;
      }
    }
  });

  document.getElementById('subtotal-personnes').textContent = subtotalPersonnes.toFixed(2);
  document.getElementById('subtotal-marchandises').textContent = subtotalMarchandises.toFixed(2);
  document.getElementById('total-transport').textContent = (subtotalPersonnes + subtotalMarchandises).toFixed(2);
}
