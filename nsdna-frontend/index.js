var express = require('express');
var app = express();
var path = require("path");
var bodyParser = require('body-parser');
var PythonShell = require('python-shell');
var fs = require("fs");
var session = null;

var pythonOptions = {
  args: [ "skeleton" ],
  mode: 'text',
  pythonOptions: ['-u']
};

var messagesFromPox = [];
var currentLists = [];
var currentSwitches = ['127.0.0.1'];

var policies = [
  "null",
  "Drop",
  "Forward",
  "Forward and Track",
  "Duplicate",
  "Block and Report"
];

var possibleLists = [{
    desc : "Anúncios publicitários",
    addr : "lists/ads.txt",
    syn  : "ads"
  },{
    desc : "Adware e malware",
    addr : "lists/adware.txt",
    syn  : "malware"
  },{
    desc : "Pornografia",
    addr : "lists/sex.txt",
    syn  : "porn"
  },{
    desc : "Regras adicionais",
    addr : "lists/custom.txt",
    syn  : "custom"
  }
];

setInterval(function(){
  currentSwitches = fs.readFileSync('../switches.txt', 'utf-8').split('\n');
},15000);

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
  extended: true
})); 

app.use('/static', express.static(__dirname + '/static'));

app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname+'/index.html'));
});

app.get('/rules', function (req, res) {
  res.sendFile(path.join(__dirname+'/rules.html'));
});

app.get('/switches', function (req, res) {
  res.sendFile(path.join(__dirname+'/switches.html'));
});

app.get('/monitor', function (req, res) {
  res.sendFile(path.join(__dirname+'/monitor.html'));
});

app.get('/help', function (req, res) {
  res.sendFile(path.join(__dirname+'/help.html'));
});

app.get('/navbar', function (req, res) {
  res.sendFile(path.join(__dirname+'/navbar.html'));
});

app.get('/get/rules', function (req, res) {
  res.jsonp(currentLists);
});

app.get('/get/custom', function (req, res) {
  res.sendFile(path.join(__dirname+'/lists/custom.txt'));
});

app.get('/get/switches', function (req, res) {
  res.jsonp(currentSwitches);
});

app.get('/get/stdout', function (req, res) {
  res.jsonp(messagesFromPox);
});

app.post('/set/rules', function (req, res) {
  currentLists = [];
  var fullString = "";
  var currentRule = "";
  if(req.body.ads == 'on'){
    possibleLists[0].policy = req.body.adsPolicy;
    currentLists.push(possibleLists[0]);
  }
  if(req.body.malware == 'on'){
    possibleLists[1].policy = req.body.malwarePolicy;
    currentLists.push(possibleLists[1]);
  }
  if(req.body.porn == 'on'){
    possibleLists[2].policy = req.body.pornPolicy;
    currentLists.push(possibleLists[2]);
  }
  if(req.body.custom == 'on'){
    possibleLists[3].policy = req.body.customPolicy;
    currentLists.push(possibleLists[3]);
  }
  fs.writeFileSync(possibleLists[3].addr, req.body.add);
  for(var item of currentLists){
    currentRule = fs.readFileSync(item.addr, 'utf-8').replace(/\r\n?|\n/g," " + policies.indexOf(item.policy) + "\n");
    fullString += currentRule;
  }
  fs.writeFileSync("../rules.txt", fullString);
  res.redirect('/rules');
});

app.get('/server/restart', function (req, res) {
  if(session){
    session.end(function (err) {
      if (err){
        messagesFromPox.push('Error closing the server');
        messagesFromPox.push(err.traceback);
      }
      messagesFromPox.push('Finishing current session\n');
    });
  }
  messagesFromPox.push('Starting Python module\n');
  session = new PythonShell('../pox.py', pythonOptions);
  session.on('error', function (err) {
    console.log(err.traceback);
    messagesFromPox.push(err.traceback);
  });
  session.on('message', function (message) {
    console.log(message);
    messagesFromPox.push(message);
  });
  res.send('applied');
});

app.listen(80, function () {
  console.log('NSDNA Front End Listening on port 80!');
});