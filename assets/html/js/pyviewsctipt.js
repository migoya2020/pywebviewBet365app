"use strict";
 
// import dayjs   from './dayjs.min.js'
// var day = dayjs().format()

function display_c(){
    var refresh=1000; // Refresh rate in milli seconds
    setTimeout('display_ct()',refresh)
    }
 
window.addEventListener('pywebviewready', function(){
    // Display Time and  Date on load
    display_ct()

})

function display_ct() {
    var date_container = document.getElementById('local-date')
    var now = Date().toLocaleString()
    date_container.innerHTML = now;
    display_c();
     }

 
function displayTonas(tona_results_item){
    var select_tona_btn =document.getElementById("top-select-tona");
    let option_tag = document.createElement('option');
    option_tag.innerText = tona_results_item.name +": "+tona_results_item.tona_id;
    option_tag.setAttribute("value", tona_results_item.tona_id);
    
    option_tag.id =tona_results_item.tona_id;
    select_tona_btn.addEventListener("change", selectValue, false);
    // option_tag.setAttribute("onclick","selectValue()");
    // option_tag.addEventListener("click", addIdTodb, false);
    
    
    // option_tag.onclick = addIdTodb();
    // option_tag.onclick = function(){
    //     code = this.getAttribute('value');
    //             eval(code);
           
    //     }
    // Append the option tag into the parent select tag
    select_tona_btn.appendChild(option_tag); 
    // console.log(option_tag)

}
function selectValue(){
    var select = document.getElementById('top-select-tona');
    // get selected tournament id
    var value = select.options[select.selectedIndex].value;
    var tonaName = select.options[select.selectedIndex].text;
    console.log(value); 
    console.log(tonaName); 
    // Display Tona name in the Middle
    var tona_name_tag =document.getElementById("show-selected-tona");
    tona_name_tag.innerText =tonaName
    tona_name_tag.style.visibility = 'visible';
    // Save the selected  tona to the localDB
    pywebview.api.setCurrentTonamentToDb(value).then(function(response) {
        showCurrentSelectedTonaDetails(response);
    });
}

function makeLight() {
    notify_pop =document.getElementsByClassName('notifypop')
    nofify_pop.classList.add("is-light")
}
// var default_tag = document.getElementById('notification-default');
// default_tag.style.visibility = 'hidden';

// window.addEventListener('pywebviewready', function() {
//     var container = document.getElementById('pywebview-status')
//     container.innerHTML = '<i>pywebview</i> is ready'
    
// })

function showCurrentSelectedTonaDetails(response) {
    var currnt_status = document.getElementById('tona-status')

    currnt_status.innerText ="SATATUS :"+response.message["tona_round_status"]
    currnt_status.style.display = 'block'
}


function  showCurrentTournaments(response){
    console.log("Show Response was logged")
    // var tournamnet_container = document.getElementById('tona-list')
    // console.log(tournamnetDiv)
    var tournamnets_array = response.message
        tournamnets_array.forEach((item) => {
            // console.log(item.name)
            displayTonas(item)
            // document.querySelector('#item-list').appendChild(p); 
        });
    // tournamnet_container.style.display = 'block'
    console.log("Done with Tona")
    
}


 
function loadTournaments() {
        pywebview.api.showTournamentsOnFrontend().then(function(response) {
            showCurrentTournaments(response)
            // console.log(response)
            });
            
        
    }
    
    
function postNotifications(message){
    var notify_section = document.getElementById('notify-section')
    // create notification element
    let notification_div = document.createElement('div');
    notification_div.classList.add("notification","is-info")
    var notify_bnt_el =document.createElement('button').classList.add("delete");
    var text_parag_tag =document.createElement("p");
    // 'first_name': 'Kevin', 'last_name': 'Kisner', 'shot': '4', 'status': 'approx', 'surface': 'OGR', 'distance': '0.483', 'time': '2021-08-14 23:34:43.028000
        text_parag_tag.innerHTML = message['time'] +": " + message['last_name'] +" "+message['first_name'] +"<br>"+ "SHOT "+message['shot'] +"STATUS :"+message['status'] +" "+ "Distance :"+ message['distance'] +"<br>" +" Surface :"+message['surface']
    //  Append kids to parents now
        notification_div.appendChild(notify_bnt_el)
        notification_div.appendChild(text_parag_tag)
        notify_section.appendChild(notification_div)
        console.log("Appended Notifications to Frontend..")
}
    
document.addEventListener('DOMContentLoaded', () => {
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
      const $notification = $delete.parentNode;
  
      $delete.addEventListener('click', () => {
        $notification.parentNode.removeChild($notification);
      });
    });
  });
 // Example POST method implementation:
// async function postData(url = './', data = {}) {
//     // Default options are marked with *
//     const response = await fetch(url, {
//       method: 'POST', // *GET, POST, PUT, DELETE, etc.
//       mode: 'no-cors', // no-cors, *cors, same-origin
//       cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
//       credentials: 'same-origin', // include, *same-origin, omit
//       headers: {
//         // 'Content-Type': 'application/json'
//         'Content-Type': 'application/x-www-form-urlencoded',
//       },
//       redirect: 'follow', // manual, *follow, error
//       referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
//       body: JSON.stringify(data) // body data type must match "Content-Type" header
//     });
    
//     return response.json(); // parses JSON response into native JavaScript objects
//   }
  
// postData('./', {  answer: 42 })
//     .then(data => {
//       console.log(data); // JSON data parsed by `data.json()` call
// });

    
// var dropdown = document.querySelector('.dropdown');
// dropdown.addEventListener('click', function(event) {
//     event.stopPropagation();
//     dropdown.classList.toggle('is-active');
// });
 
// var myHeaders = new Headers();
// myHeaders.append("Content-Type", "application/json");
// console.log(myHeaders)

// var raw = JSON.stringify({
//   "first_name": "Kevin",
//   "last_name": "Kisner",
//   "shot": "4",
//   "status": "approx",
//   "surface": "OGR",
//   "distance": "0.483",
//   "time": "2021-08-14 23:34:43.028000"
// });

// var requestOptions = {
//   method: 'POST',
//   headers: myHeaders,
//   body: raw,
//   redirect: 'follow'
// };

// fetch("http://localhost/index.html", requestOptions)
//   .then(response => response.text())
//   .then(result => console.log(result))
//   .catch(error => console.log('error', error));
