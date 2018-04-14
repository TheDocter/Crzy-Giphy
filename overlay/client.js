//---------------------------------
// Variables
//---------------------------------
var serviceUrl = "ws://127.0.0.1:3337/streamlabs"
var socket = new WebSocket(serviceUrl);

//---------------------------------
// Open Event
//---------------------------------
socket.onopen = function()
{
 // Format your Authentication Information
 var auth = {
 author: "TheCrzyDoctor",
 website: "https://twitch.tv/thecrzydoctor",
 api_key: API_Key,
 events: [
 "EVENT_GIFYCREATED"
 ]
 }

 // Send your Data to the server
 socket.send(JSON.stringify(auth));
};

//---------------------------------
// Error Event
//---------------------------------
socket.onerror = function(error)
{
 // Something went terribly wrong... Respond?!
 console.log("Error: " + error);
}


//---------------------------------
// Message Event
//---------------------------------
socket.onmessage = function (message)
{
 // You have received new data now process it
 console.log(message.data);
 ShowGify(message.data);
 //$('#gify').html(message.data);
}


//---------------------------------
// Message Event
//---------------------------------
socket.onclose = function ()
{
 // Connection has been closed by you or the server
 console.log("Connection Closed!");
}

//---------------------------------
// Display Gify Function
//---------------------------------
function ShowGify(data){
    //var div = document.getElementById('gify');
    //div.innerHTML += data.data;
    var pic = JSON.parse(data);

    if (pic["event"] === "EVENT_CONNECTED"){
        $("#gify")
        .prepend("<div>Crzay Giphy has Connected!</div>")
        .children(':first')
        .delay(5000)
        .fadeOut(100);
    }
    else{
        if (hasValue(pic)){
            $("#gify")
            .prepend("<center><div> <img src=" + pic['data'] + " width='500' height='500'></div></center>")
            .children(':first')
            .delay(5000)
            .fadeOut(100);
        }
        else{
            $("#gify")
            .prepend("<center><div> <img src='https://media3.giphy.com/media/LGVQJ4cQGPs8o/giphy.gif' width='350' height='275'></div></center>")
            .children(':first')
            .delay(5000)
            .fadeOut(100);
        }
    }

}

//----------------------------------
// Check to see if pic has any data
//----------------------------------
function hasValue(pic){
    if (pic[data] == null){
        reutrn false;
    }
    return true;
}