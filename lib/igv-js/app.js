var express = require('express')
var helmet = require('helmet')
var os = require("os")
var path = require('path')
var compression = require('compression')

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
    message3: "Hostname: " + hostname,
    genome: "hg19",
    locus: "chr8:128,747,267-128,754,546",
    tracks: [
      {
        type: 'alignment',
        sourceType: 'htsget',
        endpoint: 'https://htsnexus.rnd.dnanex.us/v1',
        id: 'BroadHiSeqX_b37/NA12878',
        name: 'NA12878'
      }]
  })
})

app.listen(80, function () {
  console.log('app listening on port 80!')
})
