function updateSelectedImagesDisplay() {
    const container = document.getElementById('selected-images');
    container.innerHTML = '';
    
    const allImages = [...selectedLocalImages, ...selectedGoogleImages];
    
    if (allImages.length === 0) {
        container.innerHTML = '<p>No images selected</p>';
        return;
    }
    
    const totalLocalImages = selectedLocalImages.length;
    
    for (let i = 0; i < allImages.length; i++) {
        const img = allImages[i];
        const div = document.createElement('div');
        div.className = 'selected-image-item';
        
        const imageType = i < totalLocalImages ? 'local' : 'google';
        
        div.innerHTML = `
            <span>${img.name}</span>
            <span class="remove-image" onclick="removeImage(${i}, '${imageType}')">×</span>
        `;
        container.appendChild(div);
    }
}

function removeImage(index, type) {
    const totalLocalImages = selectedLocalImages.length;
    
    if (type === 'local') {
        if (index < totalLocalImages) {
            selectedLocalImages.splice(index, 1);
        }
    } else {
        const googleIndex = index - totalLocalImages;
        if (googleIndex >= 0 && googleIndex < selectedGoogleImages.length) {
            selectedGoogleImages.splice(googleIndex, 1);
        }
    }
    
    updateSelectedImagesDisplay();
}

function gapiLoaded() {
    gapi.load('client:picker', initializePicker);
}

async function initializePicker() {
    await gapi.client.load('https://www.googleapis.com/discovery/v1/apis/drive/v3/rest');
    pickerInited = true;
    maybeEnableButtons();
}

function gisLoaded() {
    const clientId = ENV.CLIENT_ID;
    if (!clientId) {
        alert("Please enter your Google Client ID first");
        return;
    }
    
    tokenClient = google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: SCOPES,
        callback: '', // defined later
    });
    gisInited = true;
    maybeEnableButtons();
}


function maybeEnableButtons() {
    if (pickerInited && gisInited) {
        document.getElementById('authorize_button').disabled = false;
    }
}

function handleAuthClick() {
    const clientId = ENV.CLIENT_ID;
    const apiKey = ENV.API_KEY;
    const appId = ENV.APP_ID;
    
    if (!clientId || !apiKey || !appId) {
        alert("Please enter your Google Client ID, API Key, and App ID first");
        return;
    }
    
    if (!tokenClient) {
        gisLoaded();
        return;
    }
    
    tokenClient.callback = async (response) => {
        if (response.error !== undefined) {
            throw (response);
        }
        accessToken = response.access_token;
        document.getElementById('signout_button').style.visibility = 'visible';
        document.getElementById('authorize_button').innerText = 'Select More from Drive';
        await createPicker();
    };

    if (accessToken === null) {
        tokenClient.requestAccessToken({prompt: 'consent'});
    } else {
        // Skip display of account chooser and consent dialog for an existing session.
        tokenClient.requestAccessToken({prompt: ''});
    }
}

/**
 *  Sign out the user upon button click.
 */
function handleSignoutClick() {
    if (accessToken) {
        google.accounts.oauth2.revoke(accessToken);
        accessToken = null;
        selectedGoogleImages = [];
        updateSelectedImagesDisplay();
        document.getElementById('authorize_button').innerText = 'Select from Google Drive';
        document.getElementById('signout_button').style.visibility = 'hidden';
    }
}

/**
 *  Create and render a Picker object for searching images.
 */
function createPicker() {
    const apiKey = ENV.API_KEY;
    const appId = ENV.APP_ID;
    
    const view = new google.picker.View(google.picker.ViewId.DOCS);
    view.setMimeTypes('image/png,image/jpeg,image/jpg');
    const picker = new google.picker.PickerBuilder()
        .enableFeature(google.picker.Feature.NAV_HIDDEN)
        .enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
        .setDeveloperKey(apiKey)
        .setAppId(appId)
        .setOAuthToken(accessToken)
        .addView(view)
        .addView(new google.picker.DocsUploadView())
        .setCallback(pickerCallback)
        .build();
    picker.setVisible(true);
}

async function pickerCallback(data) {
    if (data.action === google.picker.Action.PICKED) {
        const documents = data[google.picker.Response.DOCUMENTS];
        
        for (let i = 0; i < documents.length; i++) {
            const document = documents[i];
            const fileId = document[google.picker.Document.ID];
            const fileName = document[google.picker.Document.NAME];
            const fileUrl = document[google.picker.Document.URL];
            
            // Add to selected images
            selectedGoogleImages.push({
                type: 'google',
                id: fileId,
                name: fileName,
                url: fileUrl
            });
        }
        
        updateSelectedImagesDisplay();
    }
}

function callFlaskRoute() {
    fetch('/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('message').innerText = data.message;
        })
        .catch(error => console.error('Error:', error));
}