// Constants for API endpoints
const API_BASE_URL = 'https://7n40rj72sl.execute-api.us-east-1.amazonaws.com/deploycf';
const SEARCH_ENDPOINT = '/search';
const UPLOAD_ENDPOINT = '/upload/b2store/';

// Function to make HTTP requests to the API
async function makeRequest(url, options) {
  try {
    const response = await fetch(url, options);
    return response.json();
  } catch (error) {
    console.error(error);
  }
}

// Function to handle displaying "No photos found" message
function displayNoResultsMessage() {
  const photosDiv = document.getElementById("photos_search_results");
  photosDiv.innerHTML = "";

  const message = document.createElement('p');
  message.textContent = 'No photos found';
  photosDiv.appendChild(message);
}

// Function to render photos
function renderPhotos(imagePaths) {
  const photosDiv = document.getElementById("photos_search_results");
  photosDiv.innerHTML = "";

  for (let i = 0; i < imagePaths.length; i++) {
    const photo_path = imagePaths[i];

    const photoHtml = `<figure style="display:inline-block; margin:10px; width:calc(100%/3 - 20px)">
                          <img src="${photo_path}" style="width:100%">
                          <figcaption style="text-align:center">${photo_path.split('/')[3].split('?')[0]}</figcaption>
                      </figure>`;
    photosDiv.innerHTML += photoHtml;
  }
}

// Function to handle text search
function textSearch() {
  const searchQuery = document.getElementById('search_query').value;
  const url = `${API_BASE_URL}${SEARCH_ENDPOINT}?q=${searchQuery}`;

  const options = {
    method: 'GET',
    headers: {
      "x-api-key": "IjkeYboLIQ8CkngFOhIzO4SiGSCXONa76N7SVPlj",
    },
  };

  makeRequest(url, options)
    .then(data => {
      console.log(data);
      if (data === 'No Results found') {
        displayNoResultsMessage();
      } else {
        renderPhotos(data.imagePaths);
      }
    });
}

// Function to perform a voice search
function voiceSearch() {
  const $micIcon = $('#mic_search');
  const recognition = new webkitSpeechRecognition();

  recognition.onstart = function() {
    $micIcon.text('mic_off');
  };

  recognition.onresult = function(event) {
    const query = event.results[0][0].transcript;
    $('#search_query').val(query);
    textSearch();
  };

  recognition.onerror = function(event) {
    console.error(event.error);
  };

  recognition.onend = function() {
    $micIcon.text('mic');
  };

  recognition.start();
}

// Function to handle photo upload
function uploadPhoto() {
  const uploadedFile = document.getElementById('uploaded_file').files[0];
  const customLabels = document.getElementById('custom_labels').value;
  const fileName = uploadedFile.name;
  const fileType = fileName.split('.').pop();

  const formData = new FormData();
  formData.append('file', uploadedFile);
  formData.append('labels', customLabels);

  const url = `${API_BASE_URL}${UPLOAD_ENDPOINT}${fileName}`;

  const options = {
    method: 'PUT',
    headers: {
      "x-amz-meta-customLabels": customLabels,
      "Content-Type": `image/${fileType}`,
      "x-api-key": "IjkeYboLIQ8CkngFOhIzO4SiGSCXONa76N7SVPlj"
    },
    body: uploadedFile
  };

  makeRequest(url, options)
    .then(data => console.log(data));
}
