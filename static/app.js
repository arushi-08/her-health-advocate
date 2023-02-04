class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];
    }
//    if ("webkitSpeechRecognition" in window) {
//        // Initialize webkitSpeechRecognition
//        let speechRecognition = new webkitSpeechRecognition();
//
//        // String for the Final Transcript
//        let final_transcript = "";
//
//        // Set the properties for the Speech Recognition object
//        speechRecognition.continuous = true;
//        speechRecognition.interimResults = true;
//
//        // Callback Function for the onStart Event
//        speechRecognition.onstart = () => {
//          // Show the Status Element
//          document.querySelector("#status").style.display = "block";
//        };
//        speechRecognition.onerror = () => {
//          // Hide the Status Element
//          document.querySelector("#status").style.display = "none";
//        };
//        speechRecognition.onend = () => {
//          // Hide the Status Element
//          document.querySelector("#status").style.display = "none";
//        };
//
//        speechRecognition.onresult = (event) => {
//          // Create the interim transcript string locally because we don't want it to persist like final transcript
//          let interim_transcript = "";
//
//          // Loop through the results from the speech recognition object.
//          for (let i = event.resultIndex; i < event.results.length; ++i) {
//            // If the result item is Final, add it to Final Transcript, Else add it to Interim transcript
//            if (event.results[i].isFinal) {
//              final_transcript += event.results[i][0].transcript;
//            } else {
//              interim_transcript += event.results[i][0].transcript;
//            }
//          }
//
//          // Set the Final transcript and Interim transcript.
//          document.querySelector("#final").innerHTML = final_transcript;
//          document.querySelector("#interim").innerHTML = interim_transcript;
//        };
//
//        // Set the onClick property of the start button
//        document.querySelector("#start").onclick = () => {
//          // Start the Speech Recognition
//          speechRecognition.start();
//        };
//        // Set the onClick property of the stop button
//        document.querySelector("#stop").onclick = () => {
//          // Stop the Speech Recognition
//          speechRecognition.stop();
//        };
//      } else {
//        console.log("Speech Recognition Not Available");
//      }
    
    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        fetch('http://127.0.0.1:8000/api/talk', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json'
            },
          })
          .then(r => r.json())
          .then(r => {
            let msg2 = { name: "Maya", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            textField.value = ''

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
          });
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Maya")
            {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            }
            else
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
          });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}


const chatbox = new Chatbox();
chatbox.display();
