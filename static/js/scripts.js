// Function to display details for ingredients or procedure.
function showDetails(button, text) {
    // Find the closest card-wrapper and then the card to target its details section
    const details = button.closest('.card-wrapper').querySelector('.details');
    details.innerHTML = text;  // Update the details text
    details.classList.add('show');  // Show the details
}

function readURL(input) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();
  
      reader.onload = function (e) {
        $('#blah').attr('src', e.target.result).width(50).height(50);
        $('#blah').attr('style', 'visibility: visible');
      };
  
      reader.readAsDataURL(input.files[0]);
    }
  }