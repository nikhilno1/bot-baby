var API_ENDPOINT = "https://eekq9x0azg.execute-api.ap-south-1.amazonaws.com/gpt2"
var prompt_ = document.getElementById('prompt');
var button = document.getElementById('get_tweets');

var x = document.getElementById("tweet-ui");
x.style.display = "none";

function truncatePrompt(prompt){
    prompt = prompt.value + " "
    prompt = prompt.substring(0,100)
    index = prompt.lastIndexOf(" ")
    return prompt.substring(0, index)
}

function validate(str, min, max) {
    n = parseFloat(str);
    return (!isNaN(n) && n >= min && n <= max);
  }

function processResponse(response){
    //console.log("Inside processResponse") 
    //console.log(response)
    tmp = JSON.parse(response)
    msg = JSON.parse(tmp) 

    addResponse(msg)

    button.disabled = !button.disabled;
    button.style.backgroundColor = "#FF9900"
    button.textContent = "Generate tweets"
}

// function addResponse(msg) {
//     document.getElementById("results").textContent = ""
//     var para = document.createElement("div");
//     var s = "<div class='center' id='gpt2'> <b> Here what our BOT has to say... </b> </br></br>"
        
//      i = 1
//      for (var key in msg){
//          var value = msg[key];
//          console.log(value);
//          s = s + i + ") " + " <b>" + value + "</b> </br></br>"
//          i = i + 1
//      }
//     para.innerHTML = s + "</div>";
//     document.getElementById('append').appendChild(para);
//   }

function addResponse(msg) {
    i = 1;
    var x = document.getElementById("tweet-ui");
    x.style.display = "block";
    var articleNode = document.querySelector(".tweet-body");
    var clone = articleNode.cloneNode(true);
    
    msg.sort(() => Math.random() - 0.5);
    for (var key in msg) {
      var value = msg[key];
      var clone = articleNode.cloneNode(true);
      var title = clone.querySelector(".tweet-text");
      title.innerText = value;
      document.getElementById("append").appendChild(clone);
    }
}

button.addEventListener('click', function() {    
    if(prompt_.value.length==0){
        alert("Your text prompt is empty! Please trigger the model with at least one word.");
        return false
    }

    prompt = truncatePrompt(prompt_)
    var inputData = {"prompt": prompt}

    //console.log(inputData)
    button.disabled = true;
    button.style.backgroundColor = "#ffc477"
    button.textContent = "Fetching"

    //element = document.getElementById('gpt2') 
    //if(element!=null){element.parentNode.removeChild(element)}
    //document.getElementById("results").textContent = "Hold on, checking if our BOT baby needs to be woken up..."
    
    var form = new FormData();
    var settings = {
    "url": "https://eekq9x0azg.execute-api.ap-south-1.amazonaws.com/gpt2?prompt="+prompt,
    "method": "POST",
    "timeout": 0,
    "headers": {
        "Content-Type": "application/json"
    },
    "processData": false,
    "mimeType": "multipart/form-data",
    "contentType": false,
    "data": form,
    "success": processResponse
    };
    $.ajax(settings).done(function (response) {
        //console.log(response);
      });

    // $.ajax({
    //     type: 'POST',
    //     // make sure you respect the same origin policy with this url:
    //     // http://en.wikipedia.org/wiki/Same_origin_policy
    //     url: API_ENDPOINT,
    //     contentType: "application/json",
    //     data: {
    //         "queryStringParameters": {
    //           "prompt": "I cat"              
    //         }
    //     },
    //     success: function(msg){
    //         alert('wow' + msg);
    //     }
    // });

    // $.ajax({
    //     url: API_ENDPOINT,
    //     type: 'POST',        
    //     tryCount : 0,
    //     retryLimit : 1,
    //     dataType: 'json',
    //     contentType: "application/json",
    //     data: JSON.stringify(inputData),
    //     success: processResponse,
    //     error: function(xhr, status, error) {
    //         console.log("AJAX status:" + status)
    //         console.log("retry " + this.tryCount + " of " + this.retryLimit)
    //         if (status == 'error') {
    //             this.tryCount++;
    //             if (this.tryCount <= this.retryLimit) {
    //                 //try again
    //                 $.ajax(this);
    //                 if (this.tryCount==1){document.getElementById("results").textContent = "Found him! Waking him up..."}
    //                 if (this.tryCount==2){document.getElementById("results").textContent = "Finding inspiration..."}
    //                 if (this.tryCount==3){document.getElementById("results").textContent = "It is hard to come up with something cool..."}
    //                 if (this.tryCount==4){document.getElementById("results").textContent = "Don't give up! We are almost there..."}
    //                 if (this.tryCount==5){document.getElementById("results").textContent = "Ok, I admit he is being slow..."}
    //                 if (this.tryCount==6){document.getElementById("results").textContent = "I hear some typing!"}
    //                 if (this.tryCount>=7){document.getElementById("results").textContent = "Still nothing?"}
    //                 return;
    //             }
    //             document.getElementById("results").textContent = "Ouch... Sorry, it seems our BOT baby is not in the mood right now ! Can you try again in a couple of minutes?";            
    //             return;
    //         }            
    //     }
    // });
}, false);
