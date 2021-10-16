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
    // console.log(value); 
    // console.log(tonaName); 
    // Display Tona name in the Middle
    var tona_name_tag =document.getElementById("show-selected-tona");
    tona_name_tag.innerText =tonaName
    tona_name_tag.style.visibility = 'visible';
    // Save the selected  tona to the localDB
    pywebview.api.setCurrentTonamentToDb(value).then(function(response) {
        // console.log('showCurrentSelectedTonaDetails')
        // console.log(response);
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
    var currnt_round_status = document.getElementById('tona-round-status')
    var currnt_tona_round = document.getElementById('tona-round')
    var currnt_tona_start = document.getElementById('tona-start')
    var currnt_tona_end = document.getElementById('tona-end')

    currnt_tona_round.innerHTML ="<b> ROUND :</b>"+response['tona_round']
    currnt_round_status.innerHTML ="<b> STATUS: </b> "+response["tona_round_status"]
    
    currnt_tona_start.innerHTML ="<b> START DATE : </b>"+response['start_time']
    currnt_tona_end.innerHTML ="<b> END DATE :</b>"+response['end_time']
    // currnt_status.style.display = 'block'
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
     //Disable Load Tounaments once its clicked.
     disableBtn()
}


// function addClickEventToNotifications(){
   
//     document.addEventListener('DOMContentLoaded', () => {
//         (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
//           const $notification = $delete.parentNode;
      
//           $delete.addEventListener('click', () => {
//             $notification.parentNode.removeChild($notification);
//           });
//         });
//       });
     
//     }
function addClickEventToNotifications(){
        (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
            const $notification = $delete.parentNode;
        
            $delete.addEventListener('click', () => {
            $notification.parentNode.removeChild($notification);
            });
        });
    }

function enableBtn(){
  var tona_btn =document.getElementById("load_tona_btn");
  tona_btn.innerHTML="Load Tournaments";
  tona_btn.removeAttribute('disabled');
}

function disableBtn(){
  var tona_btn =document.getElementById("load_tona_btn");
  tona_btn.innerHTML="Tournaments Loaded"
  tona_btn.setAttribute('disabled','')
}


function addClickEventToTable(){
  var table = document.getElementById("tona_palyers_table");
  var rows = table.querySelectorAll("tr");
  rows.forEach(row => {
    
    row.addEventListener('click', () => {
      var id_cell = row.getElementsByTagName("td")[0];
      var player_id = id_cell.innerHTML;
      pywebview.api.addRemovePlayerFromNotifications(player_id).then(function(response) {
        row.classList.toggle('is-selected');
        console.log(response)
        });
      
    });
  });
  }
 

function loadTournaments() {
        pywebview.api.showTournamentsOnFrontend().then(function(response) {
            showCurrentTournaments(response)
           
            });         
    }

function showTournamentTable(tona_html){
    var parser = new DOMParser;
    var table_dom = parser.parseFromString(tona_html,'text/html');
    var decodedString = table_dom.body.textContent;
    var ton_div = document.getElementById('tonas_table');
    ton_div.innerHTML= decodedString;
}

function showTonaPlayersTable(players_html_table){
  var parser = new DOMParser;
  var table_dom = parser.parseFromString(players_html_table,'text/html');
  var decodedString = table_dom.body.textContent;
  var ton_div = document.getElementById('tona_palyers_table');
  ton_div.innerHTML= decodedString;
  var switchBtn = document.getElementById("switchPar_div");
  switchBtn.style.display = 'block';
  addClickEventToTable()
}

    
let tabsWithContent = (function () {
    let tabs = document.querySelectorAll('.tabs li');
    let tabsContent = document.querySelectorAll('.tab-content');
  
    let deactvateAllTabs = function () {
      tabs.forEach(function (tab) {
        tab.classList.remove('is-active');
      });
    };
  
    let hideTabsContent = function () {
      tabsContent.forEach(function (tabContent) {
        tabContent.classList.remove('is-active');
      });
    };
  
    let activateTabsContent = function (tab) {
      tabsContent[getIndex(tab)].classList.add('is-active');
    };
  
    let getIndex = function (el) {
      return [...el.parentElement.children].indexOf(el);
    };
  
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        deactvateAllTabs();
        hideTabsContent();
        tab.classList.add('is-active');
        activateTabsContent(tab);
      });
    })
  
    tabs[0].click();
  })();
  

//  Switch Par Notificatiosn On/Off

function switchPar(){
  // var switchBtn = document.getElementById("switchPar");
  pywebview.api.turnParOn_Off().then(function(response) {
    console.log(response);
   
    });

}