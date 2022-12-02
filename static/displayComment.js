const handleChange = (choix, correct) => {
  if (choix === correct)
  {
    document.getElementById('comment').classList.remove('d-none');
    document.getElementById('#comment').classList.add('d-block');
  }
}
