var express = require('express')
var helmet = require('helmet')
var os = require("os")
var path = require('path')
var compression = require('compression')
var igv = require('igv.min')

var app = express()
var hostname = os.hostname()
var p = path.join(__dirname, '/html')

app.use(helmet())
app.use(express.static(p))
app.use(compression())
app.set('views', p)
app.set('view engine', 'pug')

app.get('/', function (req, res) {
  res.render('index', {
    title: 'igv.js Demo App v1',
    message1: 'IGV.js Web App',
    message2: 'App Version: v1',
    message3: "Hostname: " + hostname
  })
})

app.listen(80, function () {
  console.log("app listening on port 80!')
})
