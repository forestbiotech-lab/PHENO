/**
 * Created by Bruno Costa on 20-06-2018.
 */

var fmtWhereAttr = require('./../helpers/formatWhereAttribute');
var controller = require('./../controllers/callController_v1.3');
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
var callStructure = require('./../structures/v1.3/calls');
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

module.exports = function(options){
  var options= options || {body:{},params:{},query:{}};  
  options.where={}


//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  call="calls"
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  //Where logic
  //Do this for each where attribute needed.
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  attribute=options.params.version
  attribute==1 ? attribute=null : null
  if (attribute != null){
    options.where["$Version.version$"]=fmtWhereAttr(attribute,"eq") 
    delete options.params.version;
  }
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

  return controller(options,call,callback)
  
}

function callback(res){
  //[The attribute in main table used as uniqueId]
  var attribute="id"
    //Metadata
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    var metadata={}
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  return {metadata:metadata,attribute:attribute,callStructure:callStructure};
}