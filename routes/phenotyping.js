var express = require('express');
var router = express.Router();
var debug = require('debug')
var debug_std = debug('brapi:server');
var debug_full= debug('brapi:trace');


router.get('/setup',function(req,res,next){
   res.render('setup',req.params)
})

router.get('/plant/set/:study/:plot/:block/:row/:pot',function(req,res,next){
   res.render('plant2',req.params)
})

module.exports = router;