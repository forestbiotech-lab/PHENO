var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var mysql = require('mysql');
var passport = require('passport');
var fs = require('fs');

// Declaring Route files
var api= {
	v1:require('./routes/api'),
	v1_3:require('./routes/api_v1.3'),
}
//var noauth = require('./routes/noauth');
var index = require('./routes/index');
var brapi = require('./routes/brapi');
var datasets = require('./routes/datasets');
var tableview = require('./routes/tableview');
var phenotyping = require('./routes/phenotyping')


// redirect stdout / stderr
if (process.env.mode=="PRODUCTION") process.__defineGetter__('stdout', function() { return fs.createWriteStream('/var/log/brapiServer.log', {flags:'a'}) })


var app = express();
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');


// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
if (process.env.mode=="PRODUCTION") process.env.log="combined"

app.use(logger(process.env.log || 'dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(require('express-session')({ secret: 'keyboard cat', resave: true, saveUninitialized: true }));
//-------For oauth--------
app.use(passport.initialize());
app.use(passport.session());
//-----End for oauth------

//Routing to specific route files depending on the incomming url.

//the default in use
app.use('/brapi/v1', api.v1_3);
app.use('/brapi/v1', api.v1);
app.use('/brapi/datasets',  datasets)
app.use('/brapi',  brapi)
app.use('/tableview/brapi/v1',  tableview)
app.use('/phenotyping',  phenotyping)
///---------------------Testing routes------------------------
//Experiment for no auth   
//app.use('/noauth/brapi/v1', noauth);
app.use('/', index);
//app.use('/users', users)
/// ------------------End testing routes----------------------


// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
