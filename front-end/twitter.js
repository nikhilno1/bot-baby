const API_ENDPOINT = "https://eekq9x0azg.execute-api.ap-south-1.amazonaws.com/gpt2"
const prompt_ = document.querySelector('#prompt');
const button = document.querySelector('#get_tweets');
const tweetArea = document.querySelector('#tweet-area')
const overlay = document.querySelector('.bg-overlay')
const overlayContent = document.querySelector('.overlay-content')
const rendered = {
  'left': false,
  'right':false
}

var input = document.getElementById("prompt");
input.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
   event.preventDefault();   
   document.getElementById("get_tweets").click();
  }
});

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function fetchRetry(url, delay, limit, fetchOptions = {}) {
  return new Promise((resolve,reject) => {
      function success(response) {
          resolve(response);
      }
      function failure(error){
          limit--;
          if(limit){
              setTimeout(fetchUrl,delay)
          }
          else {
              // this time it failed for real
              reject(error);
          }
      }
      function finalHandler(finalError){
          throw finalError;
      }
      function fetchUrl() {
          return fetch(url,fetchOptions)
              .then(success)
              .catch(failure)
              .catch(finalHandler);
      }
      fetchUrl();
  });
}

button.addEventListener('click', () => {
    if (prompt_.value.length == 0){ 
        alert("Your text prompt is empty! Please trigger the model with at least one word.");
        return false
    }
    prompt = truncatePrompt(prompt_)

    button.disabled = true;
    button.style.backgroundColor = "#ffc477"
    button.textContent = "Running";

    clearDataFromUI()
    showSpinner()
    var models = ["left", "right"];
    models.forEach(function(model) {
   
      fetchRetry(`${API_ENDPOINT}?prompt=${prompt}&model=${model}`, 10000,6, {
        method: 'GET',
        headers: { 'content-type': 'application/json' },

      }).then((response) =>{
          return response.json()
      }).then((data) => {
          return JSON.parse(data);
      }).then((data) => {        
          //add_headline_image();

          addDataToUI(data, model);
          button.disabled = false;
          button.textContent = 'Generate'
          
          
          removeSpinner()
      }).catch(function(error){
       
      });;
    });
});

function truncatePrompt(prompt) {
    prompt = prompt.value + " "
    prompt = prompt.substring(0, 100)
    index = prompt.lastIndexOf(" ")
    return prompt.substring(0, index)
}

function showSpinner(){

    overlay.style.display = 'block';
}
function removeSpinner(){
  if(rendered['left'] && rendered['right'])
    overlay.style.display = 'none';
}

function clearDataFromUI(data, side){    
  let area = null;
  
  area = tweetArea.childNodes[1];
  area.innerHTML = "";
  area = tweetArea.childNodes[3];  
  area.innerHTML = "";
}


function addDataToUI(data, side){    
    let area = null;
    if(side === 'left'){ 
      area = tweetArea.childNodes[1];
    }else{ 
      area = tweetArea.childNodes[3];
    }
    area.innerHTML = "";
    data.sort(() => Math.random() - 0.5);
    for(i = 0; i < data.length; i++){
        d = data[i];
        addTweet(d, area, side);
    }
    rendered[side] = true
  
}

function addTweet(tweet, area, side){      
    const tweet_html = constructTweetHTML(tweet, side);
    const div =  document.createElement('div');
    div.innerHTML = tweet_html;    
    area.appendChild(div);    
}

function add_headline_image() {  
  show_image("./images/collage.jpg", 800,600, "Headline image");
}

function show_image(src, width, height, alt) {
  var img = document.createElement("img");
  img.src = src;
  img.width = width;
  img.height = height;
  img.alt = alt;
  
  var src = document.getElementById("x");
  src.appendChild(img);
}

function constructTweetHTML(tweet, side){
    if(side === 'left'){ 
      src= './images/boss-baby-left-1.png'
      username='Left-wing Baby'
      handle='@LeftWingBaby'
    }else{ 
      src = './images/boss-baby-right-3.png'
      username='Right-wing Baby'
      handle='@RightWingBaby'
    }
    return `<div id="tweet-ui" class="tweet-body max-w-xl mx-auto my-6">
    <article class="border-t border-b border-gray-400 p-2 hover:bg-gray-100 flex flex-wrap items-start cursor-pointer">
      <img src=${src} class="rounded-full w-12 h-12 mr-3" />
  
      <div class="flex flex-wrap justify-start items-start flex-1">
  
        <div class="flex flex-1 items-center">
          <div class="flex-1 flex items-center">
            <h3 class="mr-2 font-bold hover:underline">
              <a href="#">${username}</a>
            </h3>
            <span class="mr-2"><svg class="w-4 h-4" fill="#1da1f2" viewBox="0 0 24 24" aria-label="Verified account" class=""><g><path d="M22.5 12.5c0-1.58-.875-2.95-2.148-3.6.154-.435.238-.905.238-1.4 0-2.21-1.71-3.998-3.818-3.998-.47 0-.92.084-1.336.25C14.818 2.415 13.51 1.5 12 1.5s-2.816.917-3.437 2.25c-.415-.165-.866-.25-1.336-.25-2.11 0-3.818 1.79-3.818 4 0 .494.083.964.237 1.4-1.272.65-2.147 2.018-2.147 3.6 0 1.495.782 2.798 1.942 3.486-.02.17-.032.34-.032.514 0 2.21 1.708 4 3.818 4 .47 0 .92-.086 1.335-.25.62 1.334 1.926 2.25 3.437 2.25 1.512 0 2.818-.916 3.437-2.25.415.163.865.248 1.336.248 2.11 0 3.818-1.79 3.818-4 0-.174-.012-.344-.033-.513 1.158-.687 1.943-1.99 1.943-3.484zm-6.616-3.334l-4.334 6.5c-.145.217-.382.334-.625.334-.143 0-.288-.04-.416-.126l-.115-.094-2.415-2.415c-.293-.293-.293-.768 0-1.06s.768-.294 1.06 0l1.77 1.767 3.825-5.74c.23-.345.696-.436 1.04-.207.346.23.44.696.21 1.04z"></path></g></svg>
            </span>
            <span class="text-gray-600 text-sm mr-1">${handle}</span>
            <span class="text-gray-600 text-sm mr-1">&nbsp;.&nbsp;</span>
            <span class="text-gray-600 text-sm">Apr 7</span>
          </div>
          <div class="text-gray-600">
            <a href="#" class="flex w-6 h-6 bg-transparent hover:bg-blue-200 rounded-full items-center justify-center hover:text-blue-600">
              <svg viewBox="0 0 24 24" class="w-3 h-3 fill-current"><g><path d="M20.207 8.147c-.39-.39-1.023-.39-1.414 0L12 14.94 5.207 8.147c-.39-.39-1.023-.39-1.414 0-.39.39-.39 1.023 0 1.414l7.5 7.5c.195.196.45.294.707.294s.512-.098.707-.293l7.5-7.5c.39-.39.39-1.022 0-1.413z"></path></g></svg>
            </a>
          </div>
        </div>
  
        <div class="w-full">
          <p class="my-1 tweet-text">${tweet}</p>
  
            <div class="flex items-center justify-start py-2">
  
            <div class="text-gray-600 flex hover:text-blue-500 items-center mr-8">
              <a href="#" class="w-8 h-8 hover:bg-blue-200 rounded-full flex items-center justify-center hover:text-blue-500">
              <svg viewBox="0 0 24 24" class="w-5 h-5 fill-current"><g><path d="M14.046 2.242l-4.148-.01h-.002c-4.374 0-7.8 3.427-7.8 7.802 0 4.098 3.186 7.206 7.465 7.37v3.828c0 .108.044.286.12.403.142.225.384.347.632.347.138 0 .277-.038.402-.118.264-.168 6.473-4.14 8.088-5.506 1.902-1.61 3.04-3.97 3.043-6.312v-.017c-.006-4.367-3.43-7.787-7.8-7.788zm3.787 12.972c-1.134.96-4.862 3.405-6.772 4.643V16.67c0-.414-.335-.75-.75-.75h-.396c-3.66 0-6.318-2.476-6.318-5.886 0-3.534 2.768-6.302 6.3-6.302l4.147.01h.002c3.532 0 6.3 2.766 6.302 6.296-.003 1.91-.942 3.844-2.514 5.176z"></path></g></svg>
              </a>
              <span class="ml-1">1.5K</span>
            </div>
  
            <div class="text-gray-600 flex hover:text-green-500 items-center mr-8">
              <a href="#" class="w-8 h-8 hover:bg-green-200 rounded-full flex items-center justify-center hover:text-green-500">
              <svg viewBox="0 0 24 24" class="w-5 h-5 fill-current"><g><path d="M23.77 15.67c-.292-.293-.767-.293-1.06 0l-2.22 2.22V7.65c0-2.068-1.683-3.75-3.75-3.75h-5.85c-.414 0-.75.336-.75.75s.336.75.75.75h5.85c1.24 0 2.25 1.01 2.25 2.25v10.24l-2.22-2.22c-.293-.293-.768-.293-1.06 0s-.294.768 0 1.06l3.5 3.5c.145.147.337.22.53.22s.383-.072.53-.22l3.5-3.5c.294-.292.294-.767 0-1.06zm-10.66 3.28H7.26c-1.24 0-2.25-1.01-2.25-2.25V6.46l2.22 2.22c.148.147.34.22.532.22s.384-.073.53-.22c.293-.293.293-.768 0-1.06l-3.5-3.5c-.293-.294-.768-.294-1.06 0l-3.5 3.5c-.294.292-.294.767 0 1.06s.767.293 1.06 0l2.22-2.22V16.7c0 2.068 1.683 3.75 3.75 3.75h5.85c.414 0 .75-.336.75-.75s-.337-.75-.75-.75z"></path></g></svg>
              </a>
              <span class="ml-1">6.7K</span>
            </div>
  
            <div class="text-gray-600 flex hover:text-red-500 items-center mr-6">
              <a href="#" class="w-8 h-8 hover:bg-red-200 rounded-full flex items-center justify-center hover:text-red-500">
              <svg viewBox="0 0 24 24" class="w-5 h-5 fill-current"><g><path d="M12 21.638h-.014C9.403 21.59 1.95 14.856 1.95 8.478c0-3.064 2.525-5.754 5.403-5.754 2.29 0 3.83 1.58 4.646 2.73.814-1.148 2.354-2.73 4.645-2.73 2.88 0 5.404 2.69 5.404 5.755 0 6.376-7.454 13.11-10.037 13.157H12zM7.354 4.225c-2.08 0-3.903 1.988-3.903 4.255 0 5.74 7.034 11.596 8.55 11.658 1.518-.062 8.55-5.917 8.55-11.658 0-2.267-1.823-4.255-3.903-4.255-2.528 0-3.94 2.936-3.952 2.965-.23.562-1.156.562-1.387 0-.014-.03-1.425-2.965-3.954-2.965z"></path></g></svg>
              </a>
              <span class="ml-1">99.9K</span>
            </div>
  
            <div class="text-gray-600 flex hover:text-blue-500 items-center mr-6">
              <a href="#" class="w-8 h-8 hover:bg-blue-200 rounded-full flex items-center justify-center hover:text-blue-500">
                  <svg viewBox="0 0 24 24" class="w-5 h-5 fill-current"><g><path d="M17.53 7.47l-5-5c-.293-.293-.768-.293-1.06 0l-5 5c-.294.293-.294.768 0 1.06s.767.294 1.06 0l3.72-3.72V15c0 .414.336.75.75.75s.75-.336.75-.75V4.81l3.72 3.72c.146.147.338.22.53.22s.384-.072.53-.22c.293-.293.293-.767 0-1.06z"></path><path d="M19.708 21.944H4.292C3.028 21.944 2 20.916 2 19.652V14c0-.414.336-.75.75-.75s.75.336.75.75v5.652c0 .437.355.792.792.792h15.416c.437 0 .792-.355.792-.792V14c0-.414.336-.75.75-.75s.75.336.75.75v5.652c0 1.264-1.028 2.292-2.292 2.292z"></path></g></svg>
              </a>
            </div>
  
          </div>
        </div>
  
      </div>
    </article>
  </div> `
}
