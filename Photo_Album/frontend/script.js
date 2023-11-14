// Define the base URL for the API and specific endpoints
const API_BASE_URL = 'https://7n40rj72sl.execute-api.us-east-1.amazonaws.com/deploycf';
const SEARCH_ENDPOINT = '/search';
const UPLOAD_ENDPOINT = '/upload/b2store/';

// Function to handle text search
function textSearch() {
  // Get the search query from the input field
  const searchQuery = document.getElementById('search_query').value;

  // Make an HTTP GET request to the search endpoint with the search query as a parameter
  fetch(API_BASE_URL + SEARCH_ENDPOINT + '?q=' + searchQuery, {
    method: 'GET',
    headers: {
      "x-api-key": "IjkeYboLIQ8CkngFOhIzO4SiGSCXONa76N7SVPlj",
    },
  })
    .then(response => response.json())
    .then(data => {
      console.log(data);
      // Handle the case when no results are found
      if (data === 'No Results found') {
        var photosDiv = document.getElementById("photos_search_results");
        photosDiv.innerHTML = "";
        const message = document.createElement('p');
        message.textContent = 'No photos found';
        photosDiv.appendChild(message);
      } else {
        // Display search results in the specified HTML element
        var photosDiv = document.getElementById("photos_search_results");
        photosDiv.innerHTML = "";

        // Iterate through the image paths and display each photo
        for (let i = 0; i < data.imagePaths.length; i++) {
          const photo_path = data.imagePaths[i];

          const photoHtml = '<figure style="display:inline-block; margin:10px; width:calc(100%/3 - 20px)">' +
            '<img src="' + `${photo_path}` + '" style="width:100%">' +
            '<figcaption style="text-align:center">' + photo_path.split('/')[3].split('?')[0] + '</figcaption>' +
            '</figure>';
          photosDiv.innerHTML += photoHtml;
        }
      }
    })
    .catch(error => console.log(error));
}

// Function to perform a voice search
function voiceSearch() {
  // Access the mic icon and create a new speech recognition object
  const $micIcon = $('#mic_search');
  const recognition = new webkitSpeechRecognition();

  // Set up event handlers for the speech recognition
  recognition.onstart = function () {
    $micIcon.text('mic_off');
  };

  recognition.onresult = function (event) {
    // Get the transcript from the speech recognition result and perform a text search
    const query = event.results[0][0].transcript;
    $('#search_query').val(query);
    textSearch();
  };

  recognition.onerror = function (event) {
    console.error(event.error);
  };

  recognition.onend = function () {
    $micIcon.text('mic');
  };

  // Start the speech recognition process
  recognition.start();
}

// Function to handle photo upload
function uploadPhoto() {
  // Get the uploaded file and custom labels from the input fields
  const uploadedFile = document.getElementById('uploaded_file').files[0];
  const customLabels = document.getElementById('custom_labels').value;

  // Create a new FormData object and append the uploaded file and custom labels to it
  const formData = new FormData();
  formData.append('file', uploadedFile);
  formData.append('labels', customLabels);

  // Get the file name, type, and log them for debugging purposes
  const fileInput = document.getElementById('uploaded_file');
  const fileName = fileInput.value.split('\\').pop();
  const fileType = fileName.split('.').pop();
  console.log(fileName);
  console.log('file type', fileType);
  console.log('cusLab', customLabels);

  // Make an HTTP PUT request to the upload endpoint with the file and custom labels as parameters
  fetch(API_BASE_URL + UPLOAD_ENDPOINT + fileName, {
    method: 'PUT',
    headers: {
      "x-amz-meta-customLabels": customLabels,
      "Content-Type": `image/${fileType}`,
      "x-api-key": "IjkeYboLIQ8CkngFOhIzO4SiGSCXONa76N7SVPlj"
    },
    body: uploadedFile
  })
    .then(response => response)
    .then(data => console.log(data))
    .catch(error => console.log(error));
}
