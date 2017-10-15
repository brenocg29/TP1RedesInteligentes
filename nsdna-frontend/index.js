var express = require('express');
var app = express();
var path = require("path");
var bodyParser = require('body-parser');
var PythonShell = require('python-shell');
//var pyshell = new PythonShell('pox.py');

var messagesFromPox = [];

app.use(bodyParser.json());

/*
pyshell.on('message', function (message) {
  messagesFromPox.push(message);
  console.log(message);
});*/

app.use('/static', express.static(__dirname + '/static'));

app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname+'/index.html'));
});

app.get('/users', function (req, res) {
  res.sendFile(path.join(__dirname+'/users.html'));
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

});

app.get('/get/users', function (req, res) {

});

app.get('/get/switches', function (req, res) {

});

app.get('/get/stdout', function (req, res) {
  res.send(JSON.stringify(messagesFromPox));
});

app.post('/add/rules', function (req, res) {
  pyshell.send(/*?*/);
});

app.post('/add/users', function (req, res) {
  pyshell.send(/*?*/);
});

app.post('/add/switches', function (req, res) {
  pyshell.send(/*?*/);
});

app.post('/remove/rules', function (req, res) {
  pyshell.send(req.body.id);
});

app.post('/remove/users', function (req, res) {
  pyshell.send(req.body.id);
});

app.post('/remove/switches', function (req, res) {
  pyshell.send(req.body.id);
});


app.listen(80, function () {
  console.log('NSDNA Front End Listening on port 80!');
});